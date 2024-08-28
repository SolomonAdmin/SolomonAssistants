from fastapi import APIRouter, HTTPException, Query
from models.models_messages import ListMessagesResponse, CreateMessageRequest, CreateMessageResponse
from services.service_messages import list_thread_messages, create_message
import logging
from typing import Optional
import requests
from utils import get_headers

WORKATO_WEBHOOK_URL = "https://webhooks.workato.com/webhooks/rest/1fb5d9d3-777d-4084-a265-dba4e5c33fb5/threadmessagecreated"

router_messages = APIRouter(prefix="/messages", tags=["Messages"])

@router_messages.get("/list_messages/threads/{thread_id}/messages", response_model=ListMessagesResponse, operation_id="list_thread_messages")
async def list_messages_endpoint(
    thread_id: str,
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20."),
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        response = list_thread_messages(thread_id, limit, order, openai_api_key)
        return response
    except Exception as e:
        logging.error(f"Error in list_messages_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_messages.post("/create_message/threads/{thread_id}/messages", response_model=CreateMessageResponse, operation_id="create_thread_message")
async def create_message_endpoint(
    thread_id: str,
    create_message_request: CreateMessageRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        response = create_message(thread_id, create_message_request, openai_api_key=openai_api_key)

        # Prepare the payload for the Workato webhook
        webhook_payload = create_message_request.dict(exclude_unset=True)
        webhook_payload['thread_id'] = thread_id

        # Prepare the headers for the Workato webhook
        headers = get_headers(openai_api_key)

        # Construct the Workato webhook URL
        webhook_url = WORKATO_WEBHOOK_URL
        if not webhook_url:
            raise ValueError("WORKATO_WEBHOOK_URL environment variable is not set")

        # Send the payload to the Workato webhook
        webhook_response = requests.post(webhook_url, json=webhook_payload, headers=headers)
        webhook_response.raise_for_status()

        logging.info(f"Webhook response: {webhook_response.json()}")

        return response
    except ValueError as ve:
        logging.error(f"Value Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except requests.exceptions.RequestException as re:
        logging.error(f"Request Error: {re}")
        raise HTTPException(status_code=500, detail="Error sending webhook")
    except Exception as e:
        logging.error(f"Error in create_message_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")