# Databricks notebook source
from databricks.vector_search.client import VectorSearchClient

# COMMAND ----------

# MAGIC %md
# MAGIC ## What this notebook does
# MAGIC 1. Create vectore search endpoint
# MAGIC 2. Query endpoint and return document text and page number

# COMMAND ----------

# The following line automatically generates a PAT Token for authentication
client = VectorSearchClient()

client.create_endpoint(
    name="form10k_vector_search_endpoint",
    endpoint_type="STANDARD"
)

# COMMAND ----------

index = client.get_index(endpoint_name="form10k_vector_search_endpoint", index_name="databricks_examples.financial_rag.vector_index")
index.describe()

# COMMAND ----------

results = index.similarity_search(
    query_text="github copilot",
    columns=["pageNumber", "markdownText"],
    num_results=5
    )

# COMMAND ----------

for result in results:
    print(f"Page Number: {result['result']['data_array'][0][0]}")
    print(f"Content: {result['result']['data_array'][0][1]}")
