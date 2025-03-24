from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("rag-app") \
    .getOrCreate()

def does_pdf_record_exist_metadata_table(file_number, document_hash):
     """
    Checks if a record exists in the PDF metadata table.

    Args:
        file_number (str): The unique file number of the PDF.
        document_hash (str): The unique hash of the PDF.

    Returns:
        bool: True if the record exists, False otherwise.
    """
     does_exist_query = f"""
        SELECT COUNT(*)
        FROM databricks_examples.financial_rag.pdf_metadata
        WHERE fileNumber = '{file_number}'
        AND documentHash = '{document_hash}'
        """
     
     doesRecordExist = spark.sql(does_exist_query).collect()[0][0] > 0
     
     return doesRecordExist
