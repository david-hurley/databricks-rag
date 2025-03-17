from unittest.mock import MagicMock, patch
from src.utils.extract_pdf_text import extract_pdf_text

def test_extract_pdf_text():
    mock_pdf = MagicMock()
    mock_pdf.__iter__.return_value = [
        MagicMock(get_text=MagicMock(return_value="Page 1 text. This is a longer synthetic text for testing purposes. It contains multiple sentences to simulate a real PDF page.")),
        MagicMock(get_text=MagicMock(return_value="Page 2 text. Another long synthetic text example. This page also contains multiple sentences to test the function's behavior.")),
    ]

    with patch("pymupdf.open", return_value=mock_pdf):
        result = extract_pdf_text("fake_path_to_pdf.pdf")

    assert result == ["Page 1 text. This is a longer synthetic text for testing purposes. It contains multiple sentences to simulate a real PDF page.", 
                      "Page 2 text. Another long synthetic text example. This page also contains multiple sentences to test the function's behavior."]