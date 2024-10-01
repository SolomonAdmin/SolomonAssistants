from fastapi import APIRouter, HTTPException, Query, Header
from models.models_messages import ListMessagesResponse, CreateMessageRequest, CreateMessageResponse
from services.service_messages import list_thread_messages, create_message
from services.service_db import DBService
import logging
from typing import Optional

router_messages = APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)

@router_messages.get("/list_messages/threads/{thread_id}/messages", response_model=ListMessagesResponse, operation_id="list_thread_messages")
async def list_messages_endpoint(
    thread_id: str,
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20."),
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = await list_thread_messages(thread_id, limit, order, openai_api_key)
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error in list_messages_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router_messages.post("/create_message/threads/{thread_id}/messages", response_model=CreateMessageResponse, operation_id="create_thread_message")
async def create_message_endpoint(
    thread_id: str,
    create_message_request: CreateMessageRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        logger.info(f"Retrieved OpenAI API key: {openai_api_key[:4]}...{openai_api_key[-4:]}")  # Log partial key

        response = await create_message(thread_id, create_message_request, openai_api_key=openai_api_key)
        return response
    except ValueError as ve:
        logger.error(f"Value Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error in create_message_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")