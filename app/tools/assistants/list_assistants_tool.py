from typing import Dict, Any
import requests

class ListAssistantsTool:
    def execute(self, limit: int = 20, order: str = "desc") -> Dict[str, Any]:
        """
        Sends a GET request to list all assistants.

        :param limit: A limit on the number of objects to be returned (between 1 and 100)
        :param order: Sort order by created_at timestamp ('asc' or 'desc')
        :return: The response from the API as a dictionary
        """
        url = 'https://55gdlc2st8.execute-api.us-east-1.amazonaws.com/assistant/list_assistants'
        headers = {
            'Content-Type': 'application/json'
        }
        params = {
            'limit': limit,
            'order': order
        }
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_assistants",
                "description": "Retrieves a list of assistants with pagination support.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "A limit on the number of objects to be returned. Limit can range between 1 and 100.",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "order": {
                            "type": "string",
                            "description": "Sort order by the created_at timestamp of the objects.",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        }
                    }
                }
            }
        }