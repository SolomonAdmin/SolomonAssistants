from fastapi import APIRouter, HTTPException, Query
from models.models_vector_stores import CreateVectorStoreRequest, VectorStoreResponse, ListVectorStoresResponse, DeleteVectorStoreResponse
from services.service_vector_stores import create_vector_store, list_vector_stores, retrieve_vector_store, delete_vector_store
import logging
from typing import Optional

router_vector_stores = APIRouter(prefix="/vector_stores", tags=["Vector Stores"])

@router_vector_stores.post("/create_vector_store", response_model=VectorStoreResponse, operation_id="create_vector_store")
async def create_vector_store_endpoint(create_vector_store_request: CreateVectorStoreRequest):
    try:
        response = create_vector_store(create_vector_store_request)
        return response
    except Exception as e:
        logging.error(f"Error in create_vector_store_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_stores.get("/list_vector_stores", response_model=ListVectorStoresResponse, operation_id="list_vector_stores")
async def list_vector_stores_endpoint(
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100."),
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    after: Optional[str] = Query(None, description="A cursor for use in pagination. after is an object ID that defines your place in the list."),
    before: Optional[str] = Query(None, description="A cursor for use in pagination. before is an object ID that defines your place in the list.")
):
    try:
        response = list_vector_stores(limit=limit, order=order, after=after, before=before)
        return response
    except Exception as e:
        logging.error(f"Error in list_vector_stores_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_stores.get("/retrieve_vector_store/{vector_store_id}", response_model=VectorStoreResponse, operation_id="retrieve_vector_store")
async def retrieve_vector_store_endpoint(vector_store_id: str):
    try:
        response = retrieve_vector_store(vector_store_id)
        return response
    except Exception as e:
        logging.error(f"Error in retrieve_vector_store_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_vector_stores.delete("/delete_vector_store/{vector_store_id}", response_model=DeleteVectorStoreResponse, operation_id="delete_vector_store")
async def delete_vector_store_endpoint(vector_store_id: str):
    try:
        response = delete_vector_store(vector_store_id)
        return response
    except Exception as e:
        logging.error(f"Error in delete_vector_store_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")