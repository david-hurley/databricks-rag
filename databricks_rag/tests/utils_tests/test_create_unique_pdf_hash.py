from src.utils.create_unique_file_hash import create_unique_pdf_hash

def test_hash_changes_when_text_changes():
    """
    Test that the hash changes when the text changes.
    """
    file_number = "00112345"
    pdf_text_1 = "This is a sample PDF text."
    pdf_text_2 = "This is a different PDF text."

    hash_1 = create_unique_pdf_hash(file_number, pdf_text_1)
    hash_2 = create_unique_pdf_hash(file_number, pdf_text_2)

    assert hash_1 != hash_2
