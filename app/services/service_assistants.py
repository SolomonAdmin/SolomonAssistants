from openai import OpenAI
import asyncio
import logging
from fastapi import UploadFile
from models.models_assistants import CreateAssistantRequest, CreateAssistantWithToolsRequest, Assistant
from typing import Dict, Any, List, Union
import os
import httpx
from fastapi import HTTPException
import logging
import requests
from utils import get_headers
from tools import tool_registry

# TODO
# from config import get_settings
# settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def create_assistant_service(assistant: CreateAssistantRequest, openai_api_key: str = None):
    url = "https://api.openai.com/v1/assistants"
    headers = get_headers(openai_api_key)
    
    logger.info(f"Creating assistant with model: {assistant.model}")
    
    # Convert Pydantic model to dict and remove None values
    assistant_data = {k: v for k, v in assistant.dict().items() if v is not None}
    
    try:
        response = requests.post(url, headers=headers, json=assistant_data)
        print(response)
        response.raise_for_status()
        logger.info(f"Assistant created successfully: {response.json()}")
        return response.json()
    except requests.exceptions.HTTPException as e:
        logger.error(f"Failed to create assistant: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def create_assistant_with_tools(assistant_data: CreateAssistantWithToolsRequest, openai_api_key: str = None) -> Assistant:
    url = "https://api.openai.com/v1/assistants"
    headers = get_headers(openai_api_key)
    
    assistant_dict = assistant_data.dict(exclude_unset=True)
    
    try:
        response = requests.post(url, headers=headers, json=assistant_dict)
        response.raise_for_status()
        return Assistant(**response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {str(e)}")
    
def list_openai_assistants(order="desc", limit=20, openai_api_key: str = None):
    url = "https://api.openai.com/v1/assistants"
    headers = get_headers(openai_api_key)
    params = {
        "order": order,
        "limit": limit
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logger.error(f"Request Error: {err}")
        raise HTTPException(status_code=err.response.status_code if err.response else 500, 
                            detail=str(err))

def modify_openai_assistant(assistant_id: str, data: Dict[str, Any], openai_api_key: str = None):
    url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = get_headers(openai_api_key)
    
    # If tools are being updated, convert them to the correct format
    if 'tools' in data:
        data['tools'] = _get_tool_definitions(data['tools'])
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logger.error(f"Request Error: {err}")
        raise HTTPException(status_code=err.response.status_code if err.response else 500, 
                            detail=str(err))

def delete_openai_assistant(assistant_id: str, openai_api_key: str = None) -> dict:
    url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = get_headers(openai_api_key)

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logger.error(f"Request Error: {err}")
        raise HTTPException(status_code=err.response.status_code if err.response else 500, 
                            detail=str(err))

def _get_tool_definitions(tools: List[Union[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    if not tools:
        return []
    
    tool_definitions = []
    for tool in tools:
        if isinstance(tool, str):
            if tool in tool_registry:
                tool_definitions.append({
                    "type": "function",
                    "function": tool_registry[tool]().get_definition()['function']
                })
            else:
                logger.warning(f"Unknown tool: {tool}")
        elif isinstance(tool, dict):
            if 'type' in tool:
                tool_definitions.append(tool)
            else:
                logger.warning(f"Invalid tool definition: {tool}")
        else:
            logger.warning(f"Invalid tool type: {type(tool)}")
    
    return tool_definitions

# New function to get an assistant's details
def get_openai_assistant(assistant_id: str, openai_api_key: str = None) -> dict:
    url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = get_headers(openai_api_key)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logger.error(f"Request Error: {err}")
        raise HTTPException(status_code=err.response.status_code if err.response else 500, 
                            detail=str(err))

# New function to update an assistant's tools
def update_assistant_tools(assistant_id: str, tools: List[str], openai_api_key: str = None) -> dict:
    tool_definitions = _get_tool_definitions(tools)
    return modify_openai_assistant(assistant_id, {"tools": tool_definitions}, openai_api_key)