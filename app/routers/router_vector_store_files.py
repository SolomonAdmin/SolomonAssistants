from fastapi import APIRouter, HTTPException, Query, Header
from models.models_vector_store_files import CreateVectorStoreFileRequest, VectorStoreFileResponse, ListVectorStoreFilesResponse, DeleteVectorStoreFileResponse, CreateVectorStoreFileWorkatoRequest
from services.service_vector_store_files import create_vector_store_file, list_vector_store_files, delete_vector_store_file, retrieve_vector_store_file, create_vector_store_file_workato
from services.service_db import DBService
from typing import Optional
import logging

router_vector_store_files = APIRouter(prefix="/vector_stores", tags=["Vector Store Files V2"])

logger = logging.getLogger(__name__)

@router_vector_store_files.post("/create_vector_store_file/{vector_store_id}/files", response_model=VectorStoreFileResponse, operation_id="create_vector_store_file")
async def create_vector_store_file_endpoint(
    vector_store_id: str, 
    create_vector_store_file_request: CreateVectorStoreFileRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        return create_vector_store_file(vector_store_id, create_vector_store_file_request, openai_api_key)
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        raise HTTPException(status_code=errh.response.status_code, detail=errh.response.text)
    except Exception as e:
        logger.error(f"Error in create_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.get("/list_vector_store_files/{vector_store_id}/files", response_model=ListVectorStoreFilesResponse, operation_id="list_vector_store_files")
async def list_vector_store_files_endpoint(
    vector_store_id: str,
    limit: int = Query(20),
    order: str = Query("desc"),
    after: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    filter: Optional[str] = Query(None),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        return list_vector_store_files(
            vector_store_id, limit, order, after, before, filter,
            openai_api_key=openai_api_key
        )
    except Exception as e:
        logger.error(f"Error in list_vector_store_files_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.delete("/delete_vector_store_file/{vector_store_id}/files/{file_id}", response_model=DeleteVectorStoreFileResponse, operation_id="delete_vector_store_file")
async def delete_vector_store_file_endpoint(
    vector_store_id: str, 
    file_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        return delete_vector_store_file(vector_store_id, file_id, openai_api_key)
    except Exception as e:
        logger.error(f"Error in delete_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.get("/retrieve_vector_store_file/{vector_store_id}/files/{file_id}", response_model=VectorStoreFileResponse, operation_id="retrieve_vector_store_file")
async def retrieve_vector_store_file_endpoint(
    vector_store_id: str, 
    file_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        return retrieve_vector_store_file(vector_store_id, file_id, openai_api_key)
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        raise HTTPException(status_code=errh.response.status_code, detail=errh.response.text)
    except Exception as e:
        logger.error(f"Error in retrieve_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_vector_store_files.post("/create_vector_store_file_workato/{vector_store_id}/files", response_model=VectorStoreFileResponse, operation_id="create_vector_store_file_workato")
async def create_vector_store_file_workato_endpoint(
    vector_store_id: str,
    request: CreateVectorStoreFileWorkatoRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")
            
        return create_vector_store_file_workato(vector_store_id, request, openai_api_key)
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        raise HTTPException(status_code=errh.response.status_code, detail=errh.response.text)
    except Exception as e:
        logger.error(f"Error in create_vector_store_file_workato_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")