import requests
import logging
from models.models_vector_store_files import CreateVectorStoreFileRequest, VectorStoreFileResponse, ListVectorStoreFilesResponse, DeleteVectorStoreFileResponse
import os
from typing import Optional

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def create_vector_store_file(vector_store_id: str, create_vector_store_file_request: CreateVectorStoreFileRequest) -> VectorStoreFileResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    payload = create_vector_store_file_request.dict()
    logging.debug(f"Payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.debug(f"Response: {response.json()}")
        return VectorStoreFileResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh.response.text}")
        if errh.response.status_code == 400:
            logging.error(f"Bad Request: Check if the file_id is correct and exists. Response: {errh.response.text}")
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

def list_vector_store_files(vector_store_id: str, limit: int = 20, order: str = "desc", after: Optional[str] = None, before: Optional[str] = None, filter: Optional[str] = None) -> ListVectorStoreFilesResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    params = {
        "limit": limit,
        "order": order,
        "after": after,
        "before": before,
        "filter": filter
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return ListVectorStoreFilesResponse(**response.json())
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

def delete_vector_store_file(vector_store_id: str, file_id: str) -> DeleteVectorStoreFileResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return DeleteVectorStoreFileResponse(**response.json())
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

def retrieve_vector_store_file(vector_store_id: str, file_id: str) -> VectorStoreFileResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return VectorStoreFileResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh.response.text}")
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