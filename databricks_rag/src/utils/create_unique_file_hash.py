import hashlib

def create_unique_pdf_hash(file_number, pdf_text):
    """
    Create a unique hash for a PDF file based on file number and content.

    Args:
        file_number (str): Unique file number of the PDF.
        pdf_text (str): The text content of the PDF file.

    Returns:
        str: The unique hash of the PDF file.
    """
    combined_text = f"{file_number}{pdf_text}"
    unique_hash = hashlib.sha256(combined_text.encode()).hexdigest()
    
    return unique_hash