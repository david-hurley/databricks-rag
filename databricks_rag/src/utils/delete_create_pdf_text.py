from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("rag-app") \
    .getOrCreate()
    
def delete_create_pdf_text(json_metadata, pdf_markdown):
    # drop any rows with the fileNumber - easier to update in case page number/content have chanaged
    drop_query = f"""
    DELETE FROM databricks_examples.financial_rag.pdf_markdown_text
    WHERE fileNumber = '{json_metadata['fileNumber']}'
    """
    spark.sql(drop_query)

    # upsert new data
    page_data = [
        (json_metadata['fileNumber'], content.markdown, page_number + 1)
        for page_number, content in enumerate(pdf_markdown.pages)
    ]

    page_df = spark.createDataFrame(page_data, ["fileNumber", "markdownText", "pageNumber"])
    page_df.createOrReplaceTempView("page_data_view")

    insert_query = """
    INSERT INTO databricks_examples.financial_rag.pdf_markdown_text 
    (fileNumber, markdownText, pageNumber)
    SELECT fileNumber, markdownText, pageNumber FROM page_data_view
    """

    spark.sql(insert_query)

    return "pdf_text table updated"