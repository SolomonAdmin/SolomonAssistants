import requests
import logging
from models.models_vector_stores import CreateVectorStoreRequest, VectorStoreResponse, ListVectorStoresResponse, DeleteVectorStoreResponse
from typing import Optional
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def create_vector_store(create_vector_store_request: CreateVectorStoreRequest) -> VectorStoreResponse:
    url = "https://api.openai.com/v1/vector_stores"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    try:
        response = requests.post(url, headers=headers, json=create_vector_store_request.dict())
        response.raise_for_status()
        return VectorStoreResponse(**response.json())
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


def list_vector_stores(limit: int = 20, order: str = "desc", after: Optional[str] = None, before: Optional[str] = None) -> ListVectorStoresResponse:
    url = "https://api.openai.com/v1/vector_stores"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    params = {
        "limit": limit,
        "order": order
    }
    if after:
        params["after"] = after
    if before:
        params["before"] = before

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return ListVectorStoresResponse(**response.json())
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
    

def retrieve_vector_store(vector_store_id: str) -> VectorStoreResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return VectorStoreResponse(**response.json())
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

def delete_vector_store(vector_store_id: str) -> DeleteVectorStoreResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return DeleteVectorStoreResponse(**response.json())
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