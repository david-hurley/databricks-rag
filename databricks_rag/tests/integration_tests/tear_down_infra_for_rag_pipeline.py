# Databricks notebook source
import mlflow.deployments

# COMMAND ----------

# create widget parameters and defaults
dbutils.widgets.text("openai_endpoint_name", "openai_completion_endpoint")
dbutils.widgets.text("database", "financial_rag")

# retrieve widget values
endpoint_name = dbutils.widgets.get("openai_endpoint_name")
database = dbutils.widgets.get("database")

# COMMAND ----------

client = mlflow.deployments.get_deploy_client("databricks")

try:
    client.delete_endpoint(endpoint_name)
    print(f"Successfully deleted model serving endpoint {endpoint_name}")
except:
    print(f"Could not delete model serving endpoint {endpoint_name}")

# COMMAND ----------

drop_database_query = f"DROP SCHEMA IF EXISTS {database} CASCADE"
spark.sql(drop_database_query)
