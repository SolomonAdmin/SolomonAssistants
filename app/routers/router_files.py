from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query, Header
from models.models_files import UploadFileResponse, ListFilesResponse
from services.service_files import upload_file, list_files
import logging
import os
from typing import Optional

router_files = APIRouter(prefix="/files", tags=["Files V2"])

@router_files.post("/upload", response_model=UploadFileResponse, operation_id="upload_file")
async def upload_file_endpoint(
    file: UploadFile = File(...),  # The uploaded file
    purpose: str = Form("assistants"),  # The purpose of the file, defaulting to "assistants"
    openai_api_key: str = Header(...)  # The API key passed as a header
):
    try:
        # Save the uploaded file temporarily
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())

        # Upload the file to OpenAI using the API key
        response = upload_file(file_path=file_location, purpose=purpose, openai_api_key=openai_api_key)

        # Remove the temporary file
        os.remove(file_location)

        return response
    except Exception as e:
        logging.error(f"Error in upload_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_files.get("/list", response_model=ListFilesResponse, operation_id="list_files")
async def list_files_endpoint(
    purpose: Optional[str] = Query(None, description="Filter by file purpose"),
    openai_api_key: str = Header(...)  # API key passed as a header
):
    try:
        response = list_files(purpose=purpose, openai_api_key=openai_api_key)
        return response
    except Exception as e:
        logging.error(f"Error in list_files_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
