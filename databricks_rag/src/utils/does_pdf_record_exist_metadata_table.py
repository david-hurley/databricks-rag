from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("rag-app") \
    .getOrCreate()

def does_pdf_record_exist_metadata_table(file_number, document_hash):

    query = f"""
    SELECT COUNT(*)
    FROM databricks_examples.financial_rag.pdf_metadata
    WHERE fileNumber = '{file_number}'
    AND documentHash = '{document_hash}'
    """

    doesRecordExist = spark.sql(query).collect()[0][0] > 0

    return doesRecordExist
