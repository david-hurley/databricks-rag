import mlflow.deployments
import openai
import json
from pydantic import BaseModel, ValidationError
from pydantic_core import from_json
class ExpectedMetadataSchema(BaseModel):
    fileNumber: str
    companyName: str
    tradingSymbol: str
    fiscalYearEndDate: str

def get_form10k_metadata_from_pdf_text_with_llm(header_page, endpoint_name):
    """
    Get the form 10-K metadata from the header page of a 10-K filing using the LLM model.

    Args:
        header_page (str): The header page of a 10-K filing.
        endpoint_name (str): The name of the LLM managed endpoint.

    Returns:
        dict: LLM response object
    """

    client = mlflow.deployments.get_deploy_client("databricks")

    response = client.predict(
        endpoint=endpoint_name,
        inputs={
            "messages": [
                {
                    "role": "user",
                    "content": 'Based on the text provided extract commission file number, company name, trading symbol, and fiscal year end date. Output should be valid JSON with keys for fileNumber, companyName, tradingSymbol, and fiscalYearEndDate. Input text: {}'.format(header_page)
                }
            ]
        }
    )

    return response

def is_llm_response_valid(raw_response):
    """
    Check if the LLM response matches shcema.

    Args:
        raw_response (dict): The raw response from the LLM model.

    Returns:
        bool: True if the response matches the schema, False otherwise
    """
        
    try:
        ExpectedMetadataSchema.model_validate_json(raw_response['choices'][0]['message']['content'])
        return True
    except ValidationError as e:
        print("Unable to validate LLM response schema.")
        return False

def parse_valid_llm_response(raw_response):
    """
    Parse the LLM response into a dictionary.
    
    Args:
        raw_response (dict): The raw response from the LLM model.
        
    Returns:
        dict: The parsed LLM response object
    """
    json_response = from_json(raw_response['choices'][0]['message']['content'], allow_partial=False)
    json_response['fileNumber'] = int(json_response['fileNumber'].replace('-', ''))
    
    return json_response

 



 
