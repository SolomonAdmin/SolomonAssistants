from typing import Dict, Any
import requests
from .base_assistant import BaseTool

class CreateAssistantTool(BaseTool):
    def execute(self, name: str, instructions: str, model: str, solomon_consumer_key: str) -> Dict[str, Any]:
        """
        Creates a new assistant.

        :param name: The name of the assistant
        :param instructions: The instructions for the assistant
        :param model: The model to use
        :param solomon_consumer_key: User's unique API key
        :return: The response from the API
        """
        url = f'{self.base_url}/assistant/create_assistant'
        headers = self.get_headers(solomon_consumer_key)
        
        data = {
            'model': model,
            'name': name,
            'instructions': instructions,
            'metadata': {
                'created_by': 'system',
                'purpose': 'assistant_management',
                'version': '1.0'
            },
            'temperature': 0.2,
            'top_p': 0.95,
            'response_format': {
                'type': 'text'
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
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
                        },
                        "solomon_consumer_key": {
                            "type": "string",
                            "description": "User's unique API key for authentication."
                        }
                    },
                    "required": ["name", "instructions", "model", "solomon_consumer_key"]
                }
            }
        }