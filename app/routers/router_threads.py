from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from models.models_threads import ThreadsResponse, CreateThreadRequest, ThreadResponse
from services.service_threads import ThreadService
from services.service_db import DBService
import logging

router_threads = APIRouter(prefix="/thread", tags=["RDS"])

@router_threads.get("/threads/{solomon_consumer_key}", response_model=ThreadsResponse)
async def get_threads(solomon_consumer_key: str, thread_service: ThreadService = Depends(ThreadService)):
    threads = thread_service.get_threads(solomon_consumer_key)
    if not threads:
        raise HTTPException(status_code=404, detail="No threads found for the given consumer key")
    return ThreadsResponse(threads=threads)

@router_threads.post("/create", response_model=ThreadResponse, operation_id="create_thread")
async def create_thread(
    thread_data: Optional[CreateThreadRequest] = None,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        # Create thread with optional data
        thread_service = ThreadService()
        thread_dict = thread_data.dict() if thread_data else {}
        response = thread_service.create_thread_service(thread_dict, openai_api_key)
        return ThreadResponse(**response)
    except Exception as e:
        logging.error(f"Error in create_thread: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")