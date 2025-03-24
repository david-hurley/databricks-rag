from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("rag-app") \
    .getOrCreate()
    
def delete_create_pdf_text(json_metadata, pdf_markdown, database):
    """
    Deletes the existing PDF text data and inserts the new PDF text data into the UC table.

    Args:
        json_metadata (dict): The metadata of the PDF file.
        pdf_markdown (dict): The PDFMarkdown object containing the PDF text data.
        database (str): The name of the database (schema) to use.

    Returns:
        str: A message indicating the status of the operation.
    """
    # drop any rows with the fileNumber - easier to update in case page number/content have chanaged
    drop_query = f"""
    DELETE FROM databricks_examples.{database}.pdf_markdown_text
    WHERE fileNumber = '{json_metadata['fileNumber']}'
    """

    spark.sql(drop_query)

    page_data = [
        (json_metadata['fileNumber'], content.markdown, page_number + 1)
        for page_number, content in enumerate(pdf_markdown.pages)
    ]

    # create temp view of new data to merge with UC table
    page_df = spark.createDataFrame(page_data, ["fileNumber", "markdownText", "pageNumber"])
    page_df.createOrReplaceTempView("page_data_view")

    insert_query = f"""
    INSERT INTO databricks_examples.{database}.pdf_markdown_text 
    (fileNumber, markdownText, pageNumber)
    SELECT fileNumber, markdownText, pageNumber FROM page_data_view
    """

    spark.sql(insert_query)

    return "Success"