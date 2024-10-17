from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query, Header
from models.models_files import UploadFileResponse, ListFilesResponse
from services.service_files import upload_file, list_files
import logging
import os
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

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

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

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = list_files(purpose=purpose, openai_api_key=openai_api_key)
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error in list_files_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")