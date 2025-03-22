# Databricks notebook source
import mlflow.deployments

# COMMAND ----------

# MAGIC %md
# MAGIC ## What this notebook does
# MAGIC 1. Create secret scope for OpenAI and Mistral API key
# MAGIC 2. Create external model endpoint pointing to OpenAI o3-mini
# MAGIC 3. Create tables in Unity Catalog to store document metadata and text

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create secret scope for OpenAI and Mistral API key
# MAGIC
# MAGIC
# MAGIC In a terminal run the following to create a scope, add your API key, and confirm scope creation
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
# MAGIC We want to be able to test this notebook and as such be able to pass in a testing name for endpoint and tables. 

# COMMAND ----------

# create widget parameters and defaults
dbutils.widgets.text("openai_endpoint_name", "openai_completion_endpoint")
dbutils.widgets.text("catalog", "databricks_examples")
dbutils.widgets.text("database", "financial_rag")

# retrieve widget values
endpoint_name = dbutils.widgets.get("openai_endpoint_name")
catalog = dbutils.widgets.get("catalog")
database = dbutils.widgets.get("database")

print(endpoint_name, catalog, database)

# COMMAND ----------

# MAGIC %md
# MAGIC ##Create external model endpoint pointing to OpenAI o3-mini

# COMMAND ----------

client = mlflow.deployments.get_deploy_client("databricks")

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

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create tables in Unity Catalog to store document metadata and text

# COMMAND ----------

create_metadata_table_query = f"""
CREATE TABLE IF NOT EXISTS {catalog}.{database}.pdf_metadata (
    fileNumber BIGINT PRIMARY KEY,
    companyName STRING,
    tradingSymbol STRING,
    fiscalYearEndDate STRING,
    documentHash STRING
) TBLPROPERTIES (delta.enableChangeDataFeed = true);
"""

create_markdown_table_query = f"""
CREATE TABLE IF NOT EXISTS {catalog}.{database}.pdf_markdown_text (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    fileNumber BIGINT,
    markdownText STRING,
    pageNumber INT,
    FOREIGN KEY (fileNumber) REFERENCES {catalog}.{database}.pdf_metadata(fileNumber)
) TBLPROPERTIES (delta.enableChangeDataFeed = true);
"""

spark.sql(create_metadata_table_query)
spark.sql(create_markdown_table_query)
