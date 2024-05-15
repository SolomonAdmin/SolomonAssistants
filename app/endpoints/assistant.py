from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models import AssistantData, ModifyAssistantRequest
from app.services import create_assistant_service, upload_file_service, create_vector_store_service, update_assistant_vector_store_service

router = APIRouter()

@router.post("/create_assistant")
async def create_assistant(assistant_data: AssistantData):
    try:
        assistant = await create_assistant_service(assistant_data)
        return {"message": "Assistant created successfully", "assistant": assistant}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_file_for_vector_store")
async def upload_file_for_vector_store(file: UploadFile = File(...)):
    try:
        response = await upload_file_service(file)
        vector_store, file_batch = await create_vector_store_service(response['id'])
        return {"message": "File uploaded successfully", "vector_store": vector_store, "file_batch": file_batch}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_assistant_vector_store/{assistant_id}")
async def update_assistant_vector_store(assistant_id: str, vector_store_id: str):
    try:
        assistant = await update_assistant_vector_store_service(assistant_id, vector_store_id)
        return {"message": "Assistant updated with new vector store successfully", "assistant": assistant}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
