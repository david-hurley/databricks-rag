import pymupdf

def extract_pdf_text(path_to_file):
    """
    Extracts the text from the PDF file specified by the given path.

    Args:
        path_to_file (str): The path to the PDF file.

    Returns:
        list[str]: A list of strings, where each string represents the text from a PDF page 
    """
    pdf_obj = pymupdf.open(path_to_file)

    pdf_text = [page.get_text() for page in pdf_obj]

    return pdf_text

