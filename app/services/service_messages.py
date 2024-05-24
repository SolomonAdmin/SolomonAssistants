import requests
import logging
from models.models_messages import ListMessagesResponse
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def list_thread_messages(thread_id: str, limit: int = 20, order: str = "desc") -> ListMessagesResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
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
