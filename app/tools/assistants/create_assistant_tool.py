from typing import Dict, Any
import requests

class CreateAssistantTool:
    def execute(self, name: str, instructions: str, model: str) -> Dict[str, Any]:
        """
        Sends a POST request to create a new assistant.

        :param name: The name of the assistant
        :param instructions: The instructions for the assistant
        :param model: The model to use for the assistant
        :return: The response from the API as a dictionary
        """
        url = 'https://55gdlc2st8.execute-api.us-east-1.amazonaws.com/assistant/create_assistant'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'name': name,
            'instructions': instructions,
            'model': model
        }
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_assistant",
                "description": "Creates a new assistant with specified name, instructions, and model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the assistant."
                        },
                        "instructions": {
                            "type": "string",
                            "description": "The instructions that define the assistant's behavior."
                        },
                        "model": {
                            "type": "string",
                            "description": "The model to use for the assistant (e.g., 'gpt-4')."
                        }
                    },
                    "required": ["name", "instructions", "model"]
                }
            }
        }