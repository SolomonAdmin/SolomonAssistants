from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from models.models_files import UploadFileResponse, ListFilesResponse
from services.service_files import upload_file, list_files
import logging
import os
from typing import Optional

router_files = APIRouter(prefix="/files", tags=["Files V2"])

@router_files.post("/upload", response_model=UploadFileResponse)
async def upload_file_endpoint(file: UploadFile = File(...), purpose: str = Form(...)):
    try:
        # Save the uploaded file temporarily
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())

        # Upload the file to OpenAI
        response = upload_file(file_path=file_location, purpose=purpose)

        # Remove the temporary file
        os.remove(file_location)

        return response
    except Exception as e:
        logging.error(f"Error in upload_file_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_files.get("/list", response_model=ListFilesResponse)
async def list_files_endpoint(purpose: Optional[str] = Query(None, description="Filter by file purpose")):
    try:
        response = list_files(purpose=purpose)
        return response
    except Exception as e:
        logging.error(f"Error in list_files_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")