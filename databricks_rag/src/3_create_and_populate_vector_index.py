# Databricks notebook source
from databricks.vector_search.client import VectorSearchClient

# COMMAND ----------

# MAGIC %md
# MAGIC ## What this notebook does
# MAGIC Creates vector search index and endpoint to query index 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create vector search endpoint

# COMMAND ----------

client = VectorSearchClient()

client.create_endpoint(
    name="form10k_vector_search_endpoint",
    endpoint_type="STANDARD"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create vector search index
# MAGIC This will create a index and compute embeddings using defined model and source table column

# COMMAND ----------

index = client.create_delta_sync_index(
  endpoint_name="form10k_vector_search_endpoint",
  source_table_name="databricks_examples.financial_rag.pdf_markdown_text",
  index_name="databricks_examples.financial_rag.pdf_markdown_text_index",
  pipeline_type="TRIGGERED",
  primary_key="id",
  embedding_source_column="markdownText",
  embedding_model_endpoint_name="databricks-bge-large-en"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Query the index

# COMMAND ----------

results = index.similarity_search(
    query_text="github copilot",
    columns=["pageNumber", "markdownText"],
    num_results=5
    )

# COMMAND ----------

for entry in results['result']['data_array']:
    print(f"Page Number: {entry[0]}")
    print(f"Content: {entry[1]}")
    print("")
