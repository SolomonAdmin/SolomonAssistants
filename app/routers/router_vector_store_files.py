from fastapi import APIRouter, HTTPException, Query
from models.models_vector_store_files import CreateVectorStoreFileRequest, VectorStoreFileResponse, ListVectorStoreFilesResponse, DeleteVectorStoreFileResponse
from services.service_vector_store_files import create_vector_store_file, list_vector_store_files, delete_vector_store_file, retrieve_vector_store_file
from typing import Optional
import logging
import requests

router_vector_store_files = APIRouter(prefix="/vector_stores", tags=["Vector Store Files V2"])

@router_vector_store_files.post("/create_vector_store_file/{vector_store_id}/files", response_model=VectorStoreFileResponse, operation_id="create_vector_store_file")
async def create_vector_store_file_endpoint(vector_store_id: str, create_vector_store_file_request: CreateVectorStoreFileRequest):
    try:
        response = create_vector_store_file(vector_store_id, create_vector_store_file_request)
        return response
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logging.error(f"Error in create_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.get("/list_vector_store_files/{vector_store_id}/files", response_model=ListVectorStoreFilesResponse, operation_id="list_vector_store_files")
async def list_vector_store_files_endpoint(
    vector_store_id: str,
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100."),
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    after: Optional[str] = Query(None, description="A cursor for use in pagination. after is an object ID that defines your place in the list."),
    before: Optional[str] = Query(None, description="A cursor for use in pagination. before is an object ID that defines your place in the list."),
    filter: Optional[str] = Query(None, description="Filter by file status. One of in_progress, completed, failed, cancelled.")
):
    try:
        response = list_vector_store_files(vector_store_id, limit, order, after, before, filter)
        return response
    except Exception as e:
        logging.error(f"Error in list_vector_store_files_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.delete("/delete_vector_store_file/{vector_store_id}/files/{file_id}", response_model=DeleteVectorStoreFileResponse, operation_id="delete_vector_store_file")
async def delete_vector_store_file_endpoint(vector_store_id: str, file_id: str):
    try:
        response = delete_vector_store_file(vector_store_id, file_id)
        return response
    except Exception as e:
        logging.error(f"Error in delete_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.get("/retrieve_vector_store_file/{vector_store_id}/files/{file_id}", response_model=VectorStoreFileResponse, operation_id="retrieve_vector_store_file")
async def retrieve_vector_store_file_endpoint(vector_store_id: str, file_id: str):
    try:
        response = retrieve_vector_store_file(vector_store_id, file_id)
        return response
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logging.error(f"Error in retrieve_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")