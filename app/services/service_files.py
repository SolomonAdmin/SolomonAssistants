import requests
import logging
from models.models_files import UploadFileResponse, ListFilesResponse, FileContentUploadResponse, FileResponse
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

def upload_file_content(file_path: str, file_name: str, openai_api_key: str, purpose: str = "assistants") -> FileContentUploadResponse:
    url = "https://api.openai.com/v1/files"
    
    headers = {
        "Authorization": f"Bearer {openai_api_key}"
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, 'application/octet-stream'),
            'purpose': (None, purpose)
        }
        
        try:
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return FileContentUploadResponse(**response.json())
        except requests.exceptions.RequestException as err:
            logging.error(f"Request Error: {err}")
            raise
    
def get_file(file_id: str, openai_api_key: str) -> FileResponse:
    """
    Retrieve information about a specific file from OpenAI.
    
    Args:
        file_id (str): The ID of the file to retrieve
        openai_api_key (str): OpenAI API key for authentication
        
    Returns:
        FileResponse: The file object from OpenAI's response
    """
    # Use the API key to set the Authorization header
    headers = {
        "Authorization": f"Bearer {openai_api_key}"
    }
    
    url = f"https://api.openai.com/v1/files/{file_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return FileResponse(**response.json())
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