from fastapi import APIRouter, Depends, HTTPException, Header
from models.models_assistant_builder_threads import AssistantBuilderThreadsResponse, AssistantBuilderThreadCreate
from services.service_assistant_builder_threads import AssistantBuilderThreadService
import logging

router_assistant_builder_threads = APIRouter(prefix="/assistant-builder-thread", tags=["Assistant Builder Threads"])
logger = logging.getLogger(__name__)

@router_assistant_builder_threads.post("/thread")
async def create_thread(
    thread_data: AssistantBuilderThreadCreate, 
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    thread_service: AssistantBuilderThreadService = Depends(AssistantBuilderThreadService)
):
    try:
        logger.info(f"Creating assistant builder thread with ID: {thread_data.thread_id}")
        thread_data.solomon_consumer_key = solomon_consumer_key
        success = thread_service.create_thread(thread_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create thread")
            
        return {"message": "Thread created successfully", "thread_id": thread_data.thread_id}
        
    except Exception as e:
        logger.exception(f"Error creating assistant builder thread: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router_assistant_builder_threads.get("/threads/{solomon_consumer_key}", response_model=AssistantBuilderThreadsResponse)
async def get_threads(
    solomon_consumer_key: str,
    thread_service: AssistantBuilderThreadService = Depends(AssistantBuilderThreadService)
):
    threads = thread_service.get_threads(solomon_consumer_key)
    return AssistantBuilderThreadsResponse(threads=threads)

@router_assistant_builder_threads.delete("/thread/{thread_id}")
async def delete_thread(
    thread_id: str, 
    thread_service: AssistantBuilderThreadService = Depends(AssistantBuilderThreadService)
):
    success = thread_service.delete_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"message": "Thread deleted successfully"}