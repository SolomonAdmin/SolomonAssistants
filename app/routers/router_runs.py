from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Path
from models.models_runs import CreateThreadRunRequest
from models.models_messages import ListMessagesResponse
from services.service_runs import create_run_and_list_messages
import logging

router_runs = APIRouter(prefix="/runs", tags=["Runs V2"])

@router_runs.post("/create_thread_and_run", response_model=ListMessagesResponse)
async def create_thread_and_run_endpoint(
    create_thread_run_request: CreateThreadRunRequest
    ):
    try:
        # Create and run the thread, then list the messages
        messages_response = create_run_and_list_messages(create_thread_run_request)
        return messages_response
    except Exception as e:
        logging.error(f"Error in create_thread_and_run_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")