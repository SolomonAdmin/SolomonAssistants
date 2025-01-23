from typing import Dict, Any
import requests
from .base_assistant import BaseTool

class CallAgentTool(BaseTool):
    def execute(self, solomon_consumer_key: str, assistant_id: str, content: str) -> Dict[str, Any]:
        """
        Creates a thread and runs it with the specified assistant.

        Args:
            solomon_consumer_key (str): User's unique consumer key for authentication
            assistant_id (str): The ID of the assistant to run
            content (str): The content/message to be processed by the assistant

        Returns:
            Dict[str, Any]: The response from the API containing the thread messages
        """
        url = 'https://55gdlc2st8.execute-api.us-east-1.amazonaws.com/api/v2/runs/create_thread_and_run'
        
        headers = {
            'solomon-consumer-key': solomon_consumer_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "assistant_id": assistant_id,
            "thread": {
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_thread_run",
                "description": "Delegates a task to another assistant by creating a new conversation thread. Use this when you need specialized knowledge or capabilities from another assistant. The other assistant will process the provided content and return their response.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "solomon_consumer_key": {
                            "type": "string",
                            "description": "User's unique consumer key for authentication"
                        },
                        "assistant_id": {
                            "type": "string",
                            "description": "The ID of the specialized assistant to consult. Choose this based on the assistant's expertise and capabilities in their description."
                        },
                        "content": {
                            "type": "string",
                            "description": "The specific question, task, or information to be analyzed by the specialized assistant. Include any relevant context or requirements they need to provide an effective response."
                        }
                    },
                    "required": ["solomon_consumer_key", "assistant_id", "content"]
                }
            }
        }