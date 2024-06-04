from openai import OpenAI
import asyncio
import logging
from fastapi import UploadFile
from models.models_assistants import CreateAssistantRequest 
import os
import httpx
from fastapi import HTTPException
import logging
import requests
from typing import Dict, Any
from utils import get_headers

# TODO
# from config import get_settings
# settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

async def create_assistant_service(assistant: CreateAssistantRequest, openai_api_key: str = None):
    url = "https://api.openai.com/v1/assistants"
    headers = get_headers(openai_api_key)
    
    logger.info(f"Creating assistant with model: {assistant.model}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=assistant.dict())
            response.raise_for_status()
            logger.info(f"Assistant created successfully: {response.json()}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to create assistant: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def list_openai_assistants(order="desc", limit=20, openai_api_key: str = None):
    url = "https://api.openai.com/v1/assistants"
    headers = headers = get_headers(openai_api_key)
    params = {
        "order": order,
        "limit": limit
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise
    
def modify_openai_assistant(assistant_id: str, data: Dict[str, Any], openai_api_key: str = None):
    url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = get_headers(openai_api_key)
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise

def delete_openai_assistant(assistant_id: str, openai_api_key: str = None) -> dict:
    url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = get_headers(openai_api_key)

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise