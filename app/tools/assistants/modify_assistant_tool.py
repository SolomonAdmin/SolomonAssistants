from typing import Dict, Any, Optional, List
import requests

class ModifyAssistantTool:
    def execute(self, assistant_id: str, name: Optional[str] = None, 
                description: Optional[str] = None, instructions: Optional[str] = None, 
                model: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                file_ids: Optional[List[str]] = None, tools: Optional[List[Dict[str, Any]]] = None,
                temperature: Optional[float] = None, top_p: Optional[float] = None,
                response_format: Optional[Dict[str, Any]] = None,
                tool_resources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sends a POST request to modify an existing assistant.

        :param assistant_id: The ID of the assistant to modify
        :param name: Optional new name for the assistant
        :param description: Optional description of the assistant
        :param instructions: Optional new instructions for the assistant
        :param model: Optional new model for the assistant
        :param metadata: Optional metadata dictionary
        :param file_ids: Optional list of file IDs
        :param tools: Optional list of tools configurations
        :param temperature: Optional sampling temperature
        :param top_p: Optional top_p sampling parameter
        :param response_format: Optional response format configuration
        :param tool_resources: Optional tool resources configuration
        :return: The response from the API as a dictionary
        """
        url = f'https://55gdlc2st8.execute-api.us-east-1.amazonaws.com/assistant/modify_assistant/{assistant_id}'
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Build payload with only non-None values
        payload = {}
        basic_fields = {
            'name': name,
            'description': description,
            'instructions': instructions,
            'model': model,
            'metadata': metadata,
            'file_ids': file_ids,
            'temperature': temperature,
            'top_p': top_p,
            'response_format': response_format
        }
        
        for field, value in basic_fields.items():
            if value is not None:
                payload[field] = value

        # Handle tools separately
        if tools is not None:
            payload['tools'] = tools

        # Handle tool_resources separately
        if tool_resources is not None:
            processed_tool_resources = {}
            
            if 'code_interpreter' in tool_resources:
                processed_tool_resources['code_interpreter'] = {
                    'file_ids': tool_resources['code_interpreter']['file_ids']
                }
                
            if 'file_search' in tool_resources:
                processed_tool_resources['file_search'] = {
                    'vector_store_ids': tool_resources['file_search']['vector_store_ids']
                }
                
            if processed_tool_resources:
                payload['tool_resources'] = processed_tool_resources

        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_assistant",
                "description": "Modifies an existing assistant's properties.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assistant_id": {
                            "type": "string",
                            "description": "The ID of the assistant to modify."
                        },
                        "name": {
                            "type": "string",
                            "description": "The new name for the assistant.",
                            "optional": True
                        },
                        "description": {
                            "type": "string",
                            "description": "A description of the assistant.",
                            "optional": True
                        },
                        "instructions": {
                            "type": "string",
                            "description": "The new instructions that define the assistant's behavior.",
                            "optional": True
                        },
                        "model": {
                            "type": "string",
                            "description": "The new model to use for the assistant (e.g., 'gpt-4').",
                            "optional": True
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Metadata in key-value pairs.",
                            "additionalProperties": True,
                            "optional": True
                        },
                        "file_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file IDs attached to the assistant.",
                            "optional": True
                        },
                        "tools": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of tool configurations.",
                            "optional": True
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Sampling temperature between 0 and 2.",
                            "minimum": 0,
                            "maximum": 2,
                            "optional": True
                        },
                        "top_p": {
                            "type": "number",
                            "description": "Nucleus sampling parameter.",
                            "minimum": 0,
                            "maximum": 1,
                            "optional": True
                        },
                        "response_format": {
                            "type": "object",
                            "description": "Format of the assistant's response.",
                            "optional": True
                        },
                        "tool_resources": {
                            "type": "object",
                            "description": "Configuration for tool resources including code_interpreter and file_search.",
                            "properties": {
                                "code_interpreter": {
                                    "type": "object",
                                    "properties": {
                                        "file_ids": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                },
                                "file_search": {
                                    "type": "object",
                                    "properties": {
                                        "vector_store_ids": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            },
                            "optional": True
                        }
                    },
                    "required": ["assistant_id"]
                }
            }
        }