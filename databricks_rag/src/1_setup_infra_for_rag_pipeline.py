# Databricks notebook source
import mlflow.deployments

# COMMAND ----------

# MAGIC %md
# MAGIC ## What this notebook does
# MAGIC This notebook creates the infrastructure necessary to run the RAG pipeline. It is seperated from pipeline logic so that it can be called with variable parameters in different environments and in testing.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create secret scope for OpenAI and Mistral API key
# MAGIC
# MAGIC
# MAGIC In a terminal, run the following to create a scope, add your API key, and confirm scope creation
# MAGIC <br/> <br/>
# MAGIC ```
# MAGIC databricks secrets create-scope openai
# MAGIC databricks secrets put-secret openai apikey
# MAGIC databricks secrets create-scope mistral
# MAGIC databricks secrets put-secret mistral apikey
# MAGIC databricks secrets list-scopes
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch Parameter Values
# MAGIC This allows running the notebook in different environments and testing. Parameters are defined in `databricks.yml` which is part of Databricks Asset Bundle.

# COMMAND ----------

# create widget parameters and defaults
dbutils.widgets.text("openai_endpoint_name", "openai_completion_endpoint")
dbutils.widgets.text("database", "financial_rag")

# retrieve widget values
endpoint_name = dbutils.widgets.get("openai_endpoint_name")
database = dbutils.widgets.get("database")

# COMMAND ----------

# MAGIC %md
# MAGIC ##Create external model endpoint pointing to OpenAI o3-mini
# MAGIC Try to create model serving endpoint. If endpoint already exists then delete and recreate to ensure new model settings are reflected.

# COMMAND ----------

client = mlflow.deployments.get_deploy_client("databricks")

delete_endpoint = False
try:
    client.get_endpoint(endpoint_name)
    print(f"Model serving endpoint {endpoint_name} already exists, attempting to delete and recreate")
    delete_endpoint = True
except:
    print(f"Model serving endpoint {endpoint_name} does not exist, attempting to create")
    pass

if delete_endpoint:
    client.delete_endpoint(endpoint_name)
    print(f"Successfully deleted model serving endpoint {endpoint_name}")

endpoint = client.create_endpoint(
    name=endpoint_name,
    config={
        "served_entities": [
            {
                "name": "completions",
                "external_model": {
                    "name": "o3-mini",
                    "provider": "openai",
                    "task": "llm/v1/chat",
                    "openai_config": {
                        "openai_api_key": "{{secrets/openai/apikey}}",
                    },
                },
            }
        ],
    },
)

print(f"Successfully created model serving endpoint {endpoint_name}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Create database (schema), volumes, and tables
# MAGIC This would be called during integration testing or once when standing up a new environment.

# COMMAND ----------

create_schema_query = f"""
CREATE SCHEMA IF NOT EXISTS databricks_examples.{database}
"""

spark.sql(create_schema_query)

# COMMAND ----------

create_raw_pdf_volume = f"""
CREATE VOLUME IF NOT EXISTS databricks_examples.{database}.form10k_pdfs
"""

spark.sql(create_raw_pdf_volume)

create_markdown_volume = f"""
CREATE VOLUME IF NOT EXISTS databricks_examples.{database}.form10k_markdown
"""

spark.sql(create_markdown_volume)

# COMMAND ----------

create_metadata_table_query = f"""
  CREATE TABLE IF NOT EXISTS databricks_examples.{database}.pdf_metadata (
    fileNumber BIGINT PRIMARY KEY,
    companyName STRING,
    tradingSymbol STRING,
    fiscalYearEndDate STRING,
    documentHash STRING
  ) TBLPROPERTIES (delta.enableChangeDataFeed = true);
"""

create_markdown_table_query = f"""
  CREATE TABLE IF NOT EXISTS databricks_examples.{database}.pdf_markdown_text (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    fileNumber BIGINT,
    markdownText STRING,
    pageNumber INT,
    FOREIGN KEY (fileNumber) REFERENCES databricks_examples.{database}.pdf_metadata(fileNumber)
  ) TBLPROPERTIES (delta.enableChangeDataFeed = true);
"""

spark.sql(create_metadata_table_query)
spark.sql(create_markdown_table_query)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Copy Test PDF to Test Database
# MAGIC Integration tests will use sample pdf that is stored in volume (could be dev or something else, could store where you want). 

# COMMAND ----------

try:
  dbutils.fs.cp (
    f"/Volumes/databricks_examples/financial_rag/form10k_pdfs/MSFT_10K_FIRST_10PG.pdf", 
    f"/Volumes/databricks_examples/{database}/form10k_pdfs/MSFT_10K_FIRST_10PG.pdf"
    )
  print("Copied test PDF to volume")
except:
  print("Could not copy test PDF to volume")
