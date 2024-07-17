from typing import Dict, Any
import requests
import json

class WorkatoAssistantFunctionTool:
    def execute(self, data_type: str, info: str) -> str:
        """
        Sends a POST request to the Workato assistant function endpoint with specified data.

        :param data_type: The value to be sent in the request body under the key 'data_type'.
        :param info: Additional information to be sent with the request.
        :return: The response text as a string.
        """
        url = 'https://apim.workato.com/jayc0/workato_assistant_function'
        headers = {
            'API-TOKEN': 'af1d16385d51a386e715e3867b747a928c048bd3b9c7f03f5bc61aa606368e03',
            'Content-Type': 'application/json'
        }
        data = {'data_type': data_type, 'info': info}
        response = requests.post(url, json=data, headers=headers)
        return response.text

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_workato_assistant_request",
                "description": "Sends a POST request to the Workato assistant function endpoint with specified data type and information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_type": {
                            "type": "string",
                            "description": "The type of data being sent (e.g., 'contact', 'failed', etc.)."
                        },
                        "info": {
                            "type": "string",
                            "description": "Additional information to be sent with the request."
                        }
                    },
                    "required": ["data_type", "info"]
                }
            }
        }