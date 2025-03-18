from mistralai import Mistral

def convert_pdf_to_markdown_mistral(pdf_path, api_key):
    client = Mistral(api_key=api_key)

    uploaded_pdf = client.files.upload(
        file={
            "file_name": "pdf_to_process.pdf",
            "content": open(pdf_path, "rb"),
        },
        purpose="ocr"
    )  

    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
        include_image_base64=True
    )

    return ocr_response
