from fastapi import APIRouter, HTTPException, Query
from models.models_runs import CreateThreadRunRequest
from models.models_messages import ListMessagesResponse
from services.service_runs import create_run_and_list_messages, run_thread_and_list_messages
import logging
from typing import Optional

router_runs = APIRouter(prefix="/runs", tags=["Runs V2"])

@router_runs.post("/create_thread_and_run", response_model=ListMessagesResponse)
async def create_thread_and_run_endpoint(
    create_thread_run_request: CreateThreadRunRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
    ):
    try:
        # Create and run the thread, then list the messages
        messages_response = create_run_and_list_messages(create_thread_run_request, openai_api_key=openai_api_key)
        return messages_response
    except Exception as e:
        logging.error(f"Error in create_thread_and_run_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_runs.post("/run_thread_and_list_messages", response_model=ListMessagesResponse)
async def run_thread_and_list_messages_endpoint(
    thread_id: str,
    assistant_id: str,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
    ):
    try:
        # Run the thread, then list the messages
        messages_response = run_thread_and_list_messages(thread_id, assistant_id, openai_api_key=openai_api_key)
        return messages_response
    except Exception as e:
        logging.error(f"Error in run_thread_and_list_messages_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
