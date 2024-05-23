from fastapi import APIRouter, HTTPException, UploadFile, File
from services.services import create_thread_with_file_service

router = APIRouter()

@router.post("/create_thread_with_file")
async def create_thread_with_file(file: UploadFile = File(...), user_message: str = "Default user message"):
    try:
        thread = await create_thread_with_file_service(file, user_message)
        return {"message": "Thread created successfully", "thread": thread}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
