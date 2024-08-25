import requests
import logging
from models.models_messages import ListMessagesResponse, CreateMessageRequest, CreateMessageResponse
import os
from typing import Optional
from utils import get_headers

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def list_thread_messages(thread_id: str, limit: int = 20, order: str = "desc", openai_api_key: Optional[str] = None) -> ListMessagesResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = get_headers(openai_api_key)
    params = {
        "limit": limit,
        "order": order
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()
        return ListMessagesResponse(**response_json)
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

def create_message(thread_id: str, create_message_request: CreateMessageRequest, openai_api_key: str = None) -> CreateMessageResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = get_headers(openai_api_key)
    payload = create_message_request.dict(exclude_none=True)  # Exclude None values
    logging.info(f"Sending request to {url}")
    logging.info(f"Headers: {headers}")
    logging.info(f"Payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        return CreateMessageResponse(**response_json)
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        logging.error(f"Response content: {errh.response.text}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise