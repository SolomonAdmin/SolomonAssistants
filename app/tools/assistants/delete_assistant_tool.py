from typing import Dict, Any
import requests

class DeleteAssistantTool:
    def execute(self, assistant_id: str) -> Dict[str, Any]:
        """
        Sends a DELETE request to remove an existing assistant.

        :param assistant_id: The ID of the assistant to delete
        :return: The response from the API as a dictionary
        """
        url = f'https://55gdlc2st8.execute-api.us-east-1.amazonaws.com/assistant/delete_assistant/{assistant_id}'
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.delete(url, headers=headers)
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_assistant",
                "description": "Deletes an existing assistant by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assistant_id": {
                            "type": "string",
                            "description": "The ID of the assistant to delete."
                        }
                    },
                    "required": ["assistant_id"]
                }
            }
        }