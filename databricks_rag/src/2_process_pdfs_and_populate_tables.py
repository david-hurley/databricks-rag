# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

from utils.get_path_of_files_modified_in_last_day import get_path_of_files_modified_in_last_day
from utils.extract_pdf_text_basic import extract_pdf_text_basic
from utils.get_form10k_metadata_from_pdf_text_with_llm import get_form10k_metadata_from_pdf_text_with_llm, is_llm_response_valid, parse_valid_llm_response
from utils.create_unique_file_hash import create_unique_pdf_hash
from utils.convert_pdf_to_markdown_mistral import convert_pdf_to_markdown_mistral
from utils.does_pdf_record_exist_metadata_table import does_pdf_record_exist_metadata_table
from utils.create_update_pdf_metadata import create_update_pdf_metadata
from utils.delete_create_pdf_text import delete_create_pdf_text

# COMMAND ----------

# MAGIC %md
# MAGIC ## What this notebook does
# MAGIC Transforms PDF to text and determines if PDF is a new or modified document. If so, extracts metadata and markdown text using LLMs and stores results in Unity Catalog tables. 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch Parameter Values
# MAGIC This allows running the notebook in different environments and testing. Parameters are defined in `databricks.yml` which is part of Databricks Asset Bundle.
# MAGIC

# COMMAND ----------

# create widget parameters and defaults
dbutils.widgets.text("openai_endpoint_name", "openai_completion_endpoint")
dbutils.widgets.text("database", "financial_rag")

# retrieve widget values
endpoint_name = dbutils.widgets.get("openai_endpoint_name")
database = dbutils.widgets.get("database")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get files to process in RAG pipeline

# COMMAND ----------

pdfs_volume_path = f"/Volumes/databricks_examples/{database}/form10k_pdfs"
pdfs_to_process = get_path_of_files_modified_in_last_day(pdfs_volume_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run RAG Pipeline

# COMMAND ----------

for pdf_path in pdfs_to_process:

    # crude text extraction to get metadata from 1st page and create document hash
    pdf_text = extract_pdf_text_basic(pdf_path)

    # we know metadata exists on first page of form-10k
    raw_response = get_form10k_metadata_from_pdf_text_with_llm(pdf_text[0], endpoint_name)

    # pydantic validation
    isResponseValid = is_llm_response_valid(raw_response)

    if not isResponseValid:
        break

    # pydantic parsing
    json_metadata = parse_valid_llm_response(raw_response)

    # unique hash made up of file number and pdf text - tells when content changed even if file number is same
    document_hash = create_unique_pdf_hash(json_metadata['fileNumber'], "".join(pdf_text))
    json_metadata['documentHash'] = document_hash
    doesRecordExist = does_pdf_record_exist_metadata_table(json_metadata['fileNumber'], document_hash)

    if doesRecordExist:
        break

    # state of art mistral OCR model - markdown is what we want to embed in vector DB
    pdf_markdown = convert_pdf_to_markdown_mistral(pdf_path, dbutils.secrets.get(scope="mistral", key="apikey"))

    # save markdown to volume
    markdown_file_name = pdfs_to_process[0].split("/")[-1].replace(".pdf", ".md")

    with open(f"/Volumes/databricks_examples/{database}/form10k_markdown/{markdown_file_name}", "wt") as f:
        for page in pdf_markdown.pages:
            f.write(page.markdown)

    # update metadata and text tables
    create_update_pdf_metadata(json_metadata, database)
    delete_create_pdf_text(json_metadata, pdf_markdown, database)
