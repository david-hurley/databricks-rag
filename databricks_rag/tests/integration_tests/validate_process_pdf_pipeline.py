# Databricks notebook source
# create widget parameters and defaults
dbutils.widgets.text("database", "test_financial_rag")

# retrieve widget values
database = dbutils.widgets.get("database")

# COMMAND ----------

query = f"SELECT * FROM databricks_examples.{database}.pdf_metadata"
pdf_metadata = spark.sql(query)

# based on test PDF
assert pdf_metadata.count() == 1
assert pdf_metadata.select("fileNumber").first()["fileNumber"] == 137845
assert pdf_metadata.select("tradingSymbol").first()["tradingSymbol"] == "MSFT"

# COMMAND ----------

query = f"SELECT * FROM databricks_examples.{database}.pdf_markdown_text"
pdf_markdown_text = spark.sql(query)

# based on test PDF
assert pdf_markdown_text.count() == 10
