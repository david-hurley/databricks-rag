from src.utils.get_form10k_metadata_from_pdf_text_with_llm import (
    is_llm_response_valid,
    parse_valid_llm_response,
)

class TestGetForm10kMetadataFromPdfTextWithLLM:
    def test_is_llm_response_valid_valid_response(self):
        """ 
        Test that is_llm_response_valid returns True for a valid response
        """
        raw_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"fileNumber": "001-12345", "companyName": "Test Company", "tradingSymbol": "TST", "fiscalYearEndDate": "2025-12-31"}'
                    }
                }
            ]
        }

        assert is_llm_response_valid(raw_response) is True

    def test_is_llm_response_valid_invalid_response(self):
        """
        Test that is_llm_response_valid returns False for an invalid response
        """
        raw_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"fileNumber": "001-12345", "companyName": "Test Company"}'
                    }
                }
            ]
        }

        assert is_llm_response_valid(raw_response) is False

    def test_parse_valid_llm_response(self):
        """
        Test that parse_valid_llm_response returns the expected response
        """
        raw_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"fileNumber": "001-12345", "companyName": "Test Company", "tradingSymbol": "TST", "fiscalYearEndDate": "2025-12-31"}'
                    }
                }
            ]
        }

        expected_response = {
            "fileNumber": 112345,
            "companyName": "Test Company",
            "tradingSymbol": "TST",
            "fiscalYearEndDate": "2025-12-31",
        }

        assert parse_valid_llm_response(raw_response) == expected_response
