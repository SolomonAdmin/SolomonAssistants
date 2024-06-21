import requests
import logging
from models.models_files import UploadFileResponse, ListFilesResponse
import os
from typing import Optional

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def upload_file(file_path: str, purpose: str) -> UploadFileResponse:
    url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    files = {
        'file': open(file_path, 'rb'),
        'purpose': (None, purpose)
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return UploadFileResponse(**response.json())
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

def list_files(purpose: Optional[str] = None) -> ListFilesResponse:
    url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    params = {}
    if purpose:
        params['purpose'] = purpose

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return ListFilesResponse(**response.json())
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
