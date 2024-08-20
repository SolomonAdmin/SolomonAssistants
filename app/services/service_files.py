import requests
import logging
from models.models_files import UploadFileResponse, ListFilesResponse
from typing import Optional

def upload_file(file_path: str, openai_api_key: str, purpose: str = "assistants") -> UploadFileResponse:
    url = "https://api.openai.com/v1/files"
    
    # Use the API key to set the Authorization header
    headers = {
        "Authorization": f"Bearer {openai_api_key}"
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
        logging.error(f"HTTP Error: {errh}, Response Content: {response.content}")
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

def list_files(purpose: Optional[str] = None, openai_api_key: str = None) -> ListFilesResponse:
    url = "https://api.openai.com/v1/files"
    
    # Define headers for v1 API
    headers = {
        "Authorization": f"Bearer {openai_api_key}"
    }
    
    params = {}
    if purpose:
        params['purpose'] = purpose

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return ListFilesResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}, Response Content: {response.content}")
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