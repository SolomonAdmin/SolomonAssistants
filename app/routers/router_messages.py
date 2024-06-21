from fastapi import APIRouter, HTTPException, Query
from models.models_messages import ListMessagesResponse, CreateMessageRequest, CreateMessageResponse
from services.service_messages import list_thread_messages, create_message
import logging
from typing import Optional

router_messages = APIRouter(prefix="/messages", tags=["Messages"])

@router_messages.get("/list_messages/threads/{thread_id}/messages", response_model=ListMessagesResponse)
async def list_messages_endpoint(
    thread_id: str,
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20."),
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.")
):
    try:
        response = list_thread_messages(thread_id, limit, order)
        return response
    except Exception as e:
        logging.error(f"Error in list_messages_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_messages.post("/create_message/threads/{thread_id}/messages", response_model=CreateMessageResponse)
async def create_message_endpoint(
    thread_id: str,
    create_message_request: CreateMessageRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        response = create_message(thread_id, create_message_request, openai_api_key=openai_api_key)
        return response
    except Exception as e:
        logging.error(f"Error in create_message_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")