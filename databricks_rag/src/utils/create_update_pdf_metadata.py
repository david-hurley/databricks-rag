from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("rag-app") \
    .getOrCreate()
    
def create_update_pdf_metadata(json_metadata, database):
    """
    Create or update the PDF metadata in the UC table.

    Args:
        json_metadata (dict): The metadata of the PDF file.
        database (str): The name of the database (schema) to use.

    Returns:
        str: A message indicating the status of the operation.
    """
    
    # create temp view of the json metadata to merge with UC table
    json_metadata_df = spark.createDataFrame([json_metadata])
    json_metadata_df.createOrReplaceTempView("json_metadata_view")

    upsert_query = f"""
        MERGE INTO databricks_examples.{database}.pdf_metadata AS target
        USING json_metadata_view AS source
        ON target.fileNumber = source.fileNumber
        WHEN MATCHED THEN
        UPDATE SET
            companyName = source.companyName,
            tradingSymbol = source.tradingSymbol,
            fiscalYearEndDate = source.fiscalYearEndDate,
            documentHash = source.documentHash
        WHEN NOT MATCHED THEN
        INSERT (fileNumber, companyName, tradingSymbol, fiscalYearEndDate, documentHash)
        VALUES (source.fileNumber, source.companyName, source.tradingSymbol, source.fiscalYearEndDate, source.documentHash)
    """

    spark.sql(upsert_query)

    return "Success"