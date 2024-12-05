from fastapi import APIRouter, HTTPException, Query, Header
from models.models_vector_store_files import CreateVectorStoreFileRequest, VectorStoreFileResponse, ListVectorStoreFilesResponse, DeleteVectorStoreFileResponse, CreateVectorStoreFileWorkatoRequest
from services.service_vector_store_files import create_vector_store_file, list_vector_store_files, delete_vector_store_file, retrieve_vector_store_file, create_vector_store_file_workato
from services.service_db import DBService
from typing import Optional
import logging
import requests

router_vector_store_files = APIRouter(prefix="/vector_stores", tags=["Vector Store Files V2"])

logger = logging.getLogger(__name__)

@router_vector_store_files.post("/create_vector_store_file/{vector_store_id}/files", response_model=VectorStoreFileResponse, operation_id="create_vector_store_file")
async def create_vector_store_file_endpoint(
    vector_store_id: str, 
    create_vector_store_file_request: CreateVectorStoreFileRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = create_vector_store_file(vector_store_id, create_vector_store_file_request)
        return response
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Error in create_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_vector_store_files.get("/list_vector_store_files/{vector_store_id}/files", response_model=ListVectorStoreFilesResponse, operation_id="list_vector_store_files")
async def list_vector_store_files_endpoint(
    vector_store_id: str,
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100."),
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    after: Optional[str] = Query(None, description="A cursor for use in pagination. after is an object ID that defines your place in the list."),
    before: Optional[str] = Query(None, description="A cursor for use in pagination. before is an object ID that defines your place in the list."),
    filter: Optional[str] = Query(None, description="Filter by file status. One of in_progress, completed, failed, cancelled."),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = list_vector_store_files(vector_store_id, limit, order, after, before, filter)
        return response
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
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = delete_vector_store_file(vector_store_id, file_id)
        return response
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
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = retrieve_vector_store_file(vector_store_id, file_id)
        return response
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Error in retrieve_vector_store_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_vector_store_files.post(
    "/create_vector_store_file_workato/{vector_store_id}/files",
    response_model=VectorStoreFileResponse,
    operation_id="create_vector_store_file_workato"
)
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
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Error in create_vector_store_file_workato_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")