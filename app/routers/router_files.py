from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query, Header
from models.models_files import UploadFileResponse, ListFilesResponse, FileContentUploadRequest, FileContentUploadResponse, FileResponse
from services.service_files import upload_file, list_files, upload_file_content, get_file
import logging
import os
import tempfile
from typing import Optional
from services.service_db import DBService
import logging

logger = logging.getLogger(__name__)

router_files = APIRouter(prefix="/files", tags=["Files V2"])

@router_files.post("/upload", response_model=UploadFileResponse, operation_id="upload_file")
async def upload_file_endpoint(
    file: UploadFile = File(...),  # The uploaded file
    purpose: str = Form("assistants"),  # The purpose of the file, defaulting to "assistants"
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        # Save the uploaded file temporarily
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())

        # Upload the file to OpenAI using the API key
        response = upload_file(file_path=file_location, purpose=purpose, openai_api_key=openai_api_key)

        # Remove the temporary file
        os.remove(file_location)

        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error in upload_file_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router_files.get("/list", response_model=ListFilesResponse, operation_id="list_files")
async def list_files_endpoint(
    purpose: Optional[str] = Query(None, description="Filter by file purpose"),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = list_files(purpose=purpose, openai_api_key=openai_api_key)
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error in list_files_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router_files.post("/upload_file_workato", response_model=FileContentUploadResponse, operation_id="upload_file_content")
async def upload_file_content_endpoint(
    request: FileContentUploadRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        with tempfile.NamedTemporaryFile(mode='w+', suffix=f'.{request.file_type}', delete=False) as temp_file:
            temp_file.write(request.content)
            temp_file.flush()
            
            response = upload_file_content(
                file_path=temp_file.name,
                file_name=request.file_name,
                purpose=request.purpose,
                openai_api_key=openai_api_key
            )
            
        os.remove(temp_file.name)
        return response
        
    except Exception as e:
        logger.exception(f"Error in upload_file_content_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router_files.get("/{file_id}", response_model=FileResponse, operation_id="get_file")
async def get_file_endpoint(
    file_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")
        
        response = get_file(file_id=file_id, openai_api_key=openai_api_key)
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error in get_file_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")