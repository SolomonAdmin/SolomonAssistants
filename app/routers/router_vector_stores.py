from fastapi import APIRouter, HTTPException, Query, Header
from models.models_vector_stores import CreateVectorStoreRequest, VectorStoreResponse, ListVectorStoresResponse, DeleteVectorStoreResponse
from services.service_vector_stores import create_vector_store, list_vector_stores, retrieve_vector_store, delete_vector_store
from services.service_db import DBService
import logging
from typing import Optional

router_vector_stores = APIRouter(prefix="/vector_stores", tags=["Vector Stores"])

logger = logging.getLogger(__name__)

@router_vector_stores.post("/create_vector_store", response_model=VectorStoreResponse, operation_id="create_vector_store")
async def create_vector_store_endpoint(
    create_vector_store_request: CreateVectorStoreRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = create_vector_store(create_vector_store_request, openai_api_key)
        return response
    except Exception as e:
        logger.error(f"Error in create_vector_store_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_stores.get("/list_vector_stores", response_model=ListVectorStoresResponse, operation_id="list_vector_stores")
async def list_vector_stores_endpoint(
    limit: int = Query(20),
    order: str = Query("desc"),
    after: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = list_vector_stores(limit=limit, order=order, after=after, before=before, openai_api_key=openai_api_key)
        return response
    except Exception as e:
        logger.error(f"Error in list_vector_stores_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_stores.get("/retrieve_vector_store/{vector_store_id}", response_model=VectorStoreResponse, operation_id="retrieve_vector_store")
async def retrieve_vector_store_endpoint(
    vector_store_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = retrieve_vector_store(vector_store_id, openai_api_key)
        return response
    except Exception as e:
        logger.error(f"Error in retrieve_vector_store_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_vector_stores.delete("/delete_vector_store/{vector_store_id}", response_model=DeleteVectorStoreResponse, operation_id="delete_vector_store")
async def delete_vector_store_endpoint(
    vector_store_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = delete_vector_store(vector_store_id, openai_api_key)
        return response
    except Exception as e:
        logger.error(f"Error in delete_vector_store_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")