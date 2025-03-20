# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC # Enables autoreload; learn more at https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules
# MAGIC # To disable autoreload; run %autoreload 0

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
# MAGIC 1. Scan Volume for PDFs modified in last 24 hours (scheduled job)
# MAGIC 2. Extract metadata from document title page using OpenAI serving endpoint (created in notebook 1)
# MAGIC 3. Use metadata and document hash to check if document has already been processed
# MAGIC 4. If document is new or has new content then convert to markdown
# MAGIC 5. Upsert metadata and markdown to tables

# COMMAND ----------

# MAGIC %md
# MAGIC ## RAG Document Pipeline
# MAGIC

# COMMAND ----------

pdfs_volume_path = "/Volumes/databricks_examples/financial_rag/form10k_pdfs"
pdfs_to_process = get_path_of_files_modified_in_last_day(pdfs_volume_path)

# COMMAND ----------

for pdf_path in pdfs_to_process:

    # crude text extraction to get metadata from 1st page and create document hash
    pdf_text = extract_pdf_text_basic(pdf_path)

    # we know metadata exists on first page of form-10k
    raw_response = get_form10k_metadata_from_pdf_text_with_llm(pdf_text[0], "openai-completion-endpoint")

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
    with open(f"/Volumes/databricks_examples/financial_rag/form10k_markdown/{markdown_file_name}", "wt") as f:
        for page in pdf_markdown.pages:
            f.write(page.markdown)

    # update metadata and text tables
    create_update_pdf_metadata(json_metadata)
    delete_create_pdf_text(json_metadata, pdf_markdown)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check table data

# COMMAND ----------

query = "SELECT * FROM databricks_examples.financial_rag.pdf_metadata"
result_df = spark.sql(query)
display(result_df)

# 5bda4e72a9b82f27960c5d963d05b7d10802458b5911b867ac135eac91d94ab9

# COMMAND ----------

query = "SELECT * FROM databricks_examples.financial_rag.pdf_markdown_text"
result_df = spark.sql(query)
display(result_df)

# COMMAND ----------


