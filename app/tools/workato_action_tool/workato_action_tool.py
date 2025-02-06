from typing import Dict, Any
import requests
import json

class WorkatoActionTool:
    def execute(self, action_type: str, parameters: Dict[str, Any], schema: str) -> str:
        """
        Sends a POST request to the Workato action endpoint with specified action type, parameters, and schema.

        :param action_type: The specific task to execute (e.g., 'query_db', 'send_email', etc.).
        :param parameters: A dictionary containing necessary parameters for the requested action.
        :param schema: The schema to be used for the action.
        :return: The response text as a string.
        """
        url = 'https://apim.workato.com/solconsult/assistant-tools-v1/workato-root-tool'
        headers = {
            'API-TOKEN': 'Odea97039e93b574b8e94036c2b747f43462ae3aec05ca781a746152fa7107f8',
            'Content-Type': 'application/json'
        }
        data = {
            'action_type': action_type,
            'parameters': parameters,
            'schema': schema
        }
        response = requests.post(url, json=data, headers=headers)
        return response.text

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "execute_workato_action",
                "description": "Routes requests to Workato for execution, enabling limitless automation, computations, and data retrieval.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "description": "The specific task to execute (e.g., 'query_db', 'send_email', 'process_file', 'trigger_rpa')."
                        },
                        "parameters": {
                            "type": "object",
                            "description": "A flexible payload containing necessary parameters for the requested action."
                        },
                        "schema": {
                            "type": "string",
                            "description": "The schema to be used for the action."
                        }
                    },
                    "required": ["action_type", "parameters", "schema"]
                }
            }
        }