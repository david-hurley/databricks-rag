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
# MAGIC ##Create external model endpoint pointing to OpenAI o3-mini

# COMMAND ----------

client = mlflow.deployments.get_deploy_client("databricks")

endpoint = client.create_endpoint(
    name="openai-completion-endpoint",
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

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS databricks_examples.financial_rag.pdf_metadata (
# MAGIC     fileNumber BIGINT PRIMARY KEY,
# MAGIC     companyName STRING,
# MAGIC     tradingSymbol STRING,
# MAGIC     fiscalYearEndDate STRING,
# MAGIC     documentHash STRING
# MAGIC ) TBLPROPERTIES (delta.enableChangeDataFeed = true);
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS databricks_examples.financial_rag.pdf_markdown_text (
# MAGIC     id BIGINT GENERATED ALWAYS AS IDENTITY,
# MAGIC     fileNumber BIGINT,
# MAGIC     markdownText STRING,
# MAGIC     pageNumber INT,
# MAGIC     FOREIGN KEY (fileNumber) REFERENCES databricks_examples.financial_rag.pdf_metadata(fileNumber)
# MAGIC ) TBLPROPERTIES (delta.enableChangeDataFeed = true);

# COMMAND ----------


