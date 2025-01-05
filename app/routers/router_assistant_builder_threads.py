from fastapi import APIRouter, Depends, HTTPException, Header
from models.models_assistant_builder_threads import (
    AssistantBuilderThreadsResponse, 
    AssistantBuilderThreadCreate,
    AssistantIdResponse,
    AssistantBuilderIdResponse
)
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

@router_assistant_builder_threads.get(
    "/thread/{thread_id}/assistant",
    response_model=AssistantIdResponse,
    summary="Get Assistant ID for Thread"
)
async def get_assistant_id_for_thread(
    thread_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    thread_service: AssistantBuilderThreadService = Depends(AssistantBuilderThreadService)
):
    """
    Retrieves the Assistant ID associated with a Thread ID.
    
    Parameters:
        thread_id: The ID of the thread
        solomon_consumer_key: The Solomon consumer key for authentication
        
    Returns:
        AssistantIdResponse containing the assistant_id
    """
    try:
        assistant_id = thread_service.get_assistant_id(thread_id, solomon_consumer_key)
        
        if not assistant_id:
            raise HTTPException(
                status_code=404,
                detail="Assistant ID not found for the given thread ID or unauthorized access"
            )
            
        return AssistantIdResponse(assistant_id=assistant_id)
        
    except Exception as e:
        logger.exception(f"Error retrieving assistant ID for thread {thread_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router_assistant_builder_threads.get(
    "/assistant-builder/{workspace_name}",
    response_model=AssistantBuilderIdResponse,
    summary="Get Assistant Builder ID for Workspace"
)
async def get_assistant_builder_id_for_workspace(
    workspace_name: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    thread_service: AssistantBuilderThreadService = Depends(AssistantBuilderThreadService)
):
    """
    Retrieves the Assistant Builder ID for a given workspace name.
    
    Parameters:
        workspace_name: The name of the workspace
        solomon_consumer_key: The Solomon consumer key for authentication
        
    Returns:
        AssistantBuilderIdResponse containing the assistant_builder_id
    """
    try:
        assistant_builder_id = thread_service.get_assistant_builder_id(
            solomon_consumer_key=solomon_consumer_key,
            workspace_name=workspace_name
        )
        
        if not assistant_builder_id:
            raise HTTPException(
                status_code=404,
                detail="Assistant Builder ID not found for the given workspace or unauthorized access"
            )
            
        return AssistantBuilderIdResponse(assistant_builder_id=assistant_builder_id)
        
    except Exception as e:
        logger.exception(f"Error retrieving assistant builder ID for workspace {workspace_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )