from typing import Dict, Any
import requests
from .base_assistant import BaseTool

class CreateAssistantTool(BaseTool):
    # Hardcoded API token
    API_TOKEN = '3cb323833ca87933cf00c6cf1b12a25e14acc1309d8ad544b850f17deaac24b5'

    def execute(self, name: str, instructions: str, description: str, solomon_consumer_key: str, thread_id: str) -> Dict[str, Any]:
        """
        Creates a new assistant using the Workato endpoint.

        :param name: The name of the assistant
        :param instructions: The instructions for the assistant
        :param description: The description of the assistant
        :param solomon_consumer_key: User's unique consumer key
        :param thread_id: Thread ID for the request
        :return: The response from the API
        """
        url = 'https://apim.workato.com/solconsult/assistant-functions-v1/assistant-builder-functions'
        
        headers = {
            'solomon-consumer-key': solomon_consumer_key,
            'api-token': self.API_TOKEN,
            'thread_id': thread_id,
            'Content-Type': 'application/json'
        }
        
        data = {
            'name': name,
            'description': description,
            'instructions': instructions
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_assistant",
                "description": "Creates a new assistant using the Workato endpoint.",
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
                        "description": {
                            "type": "string",
                            "description": "The description of the assistant."
                        },
                        "solomon_consumer_key": {
                            "type": "string",
                            "description": "User's unique consumer key for authentication."
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Thread ID for the request."
                        }
                    },
                    "required": ["name", "instructions", "description", "solomon_consumer_key", "thread_id"]
                }
            }
        }