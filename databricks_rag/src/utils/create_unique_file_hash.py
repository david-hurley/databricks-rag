import hashlib

def create_unique_pdf_hash(file_number, pdf_text):
    combined_text = f"{file_number}{pdf_text}"
    unique_hash = hashlib.sha256(combined_text.encode()).hexdigest()
    return unique_hash