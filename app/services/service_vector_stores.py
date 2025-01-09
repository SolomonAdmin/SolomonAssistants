import requests
import logging
from models.models_vector_stores import CreateVectorStoreRequest, VectorStoreResponse, ListVectorStoresResponse, DeleteVectorStoreResponse
from typing import Optional
from utils import get_headers

logger = logging.getLogger(__name__)

def create_vector_store(create_vector_store_request: CreateVectorStoreRequest, openai_api_key: str) -> VectorStoreResponse:
    url = "https://api.openai.com/v1/vector_stores"
    headers = get_headers(openai_api_key)

    try:
        response = requests.post(url, headers=headers, json=create_vector_store_request.dict())
        response.raise_for_status()
        return VectorStoreResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        raise
    except Exception as e:
        logger.error(f"Request Error: {e}")
        raise

def list_vector_stores(limit: int = 20, order: str = "desc", after: Optional[str] = None, before: Optional[str] = None, openai_api_key: str = None) -> ListVectorStoresResponse:
    url = "https://api.openai.com/v1/vector_stores"
    headers = get_headers(openai_api_key)
    
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
    except Exception as e:
        logger.error(f"Request Error: {e}")
        raise

def retrieve_vector_store(vector_store_id: str, openai_api_key: str) -> VectorStoreResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}"
    headers = get_headers(openai_api_key)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return VectorStoreResponse(**response.json())
    except Exception as e:
        logger.error(f"Request Error: {e}")
        raise

def delete_vector_store(vector_store_id: str, openai_api_key: str) -> DeleteVectorStoreResponse:
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}"
    headers = get_headers(openai_api_key)

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return DeleteVectorStoreResponse(**response.json())
    except Exception as e:
        logger.error(f"Request Error: {e}")
        raise