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
    """ """

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
    """ """
        
    try:
        ExpectedMetadataSchema.model_validate_json(raw_response['choices'][0]['message']['content'])
        return True
    except ValidationError as e:
        print("Unable to validate LLM response schema.")
        return False

def parse_valid_llm_response(raw_response):
    """ """
    json_response = from_json(raw_response['choices'][0]['message']['content'], allow_partial=False)
    json_response['fileNumber'] = int(json_response['fileNumber'].replace('-', ''))
    return json_response

 



 
