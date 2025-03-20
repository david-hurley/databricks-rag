from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("rag-app") \
    .getOrCreate()
    
def create_update_pdf_metadata(json_metadata):
    
    json_metadata_df = spark.createDataFrame([json_metadata])

    json_metadata_df.createOrReplaceTempView("json_metadata_view")

    # update metadata if file number exists otherwise insert new
    upsert_query = """
    MERGE INTO databricks_examples.financial_rag.pdf_metadata AS target
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

    return "pdf_metadata table updated"