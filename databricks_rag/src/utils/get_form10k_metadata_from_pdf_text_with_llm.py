import mlflow.deployments
import openai
import json

def get_form10k_metadata_from_pdf_text_with_llm(header_page):

    response = openai.chat.completions.create(
        model="o3-mini",
        messages=[
            {
                "role": "user",
                "content": 'Based on the text provided extract commission file number, company name, trading symbol, and fiscal year end date. '
                'Output should be valid JSON with keys for fileNumber, companyName, tradingSymbol, and fiscalYearEndDate. '
                'Input text: {}'.format(header_page)
            }
        ]
    )

    # client = mlflow.deployments.get_deploy_client("databricks")

    # chat_response = client.predict(
    #     endpoint="openai-chat-endpoint",
    #     inputs={
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": 'Based on the text provided extract commission file number, company name, trading symbol, and fiscal year end date. Output should be valid JSON with keys for fileNumber, companyName, tradingSymbol, and fiscalYearEndDate. Input text: {}'.format(header_page)
    #             }
    #         ],
    #         "max_tokens": 1000
    #     }
    # )

    json_data = json.loads(response.choices[0].message.content)

    return json_data