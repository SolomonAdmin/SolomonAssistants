from fastapi import APIRouter, HTTPException, Query
from models.models_runs import CreateThreadRunRequest, RunThreadRequest
from models.models_messages import ListMessagesResponse
from services.service_runs import create_run_and_list_messages, run_thread_and_list_messages
import logging
from typing import Optional
from tools import tool_registry
from typing import List, Dict, Any, Union

router_runs = APIRouter(prefix="/runs", tags=["Runs V2"])

logger = logging.getLogger(__name__)

# @router_runs.post("/create_thread_and_run", response_model=ListMessagesResponse)
# async def create_thread_and_run_endpoint(
#     create_thread_run_request: CreateThreadRunRequest,
#     openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
#     ):
#     try:
#         # Create and run the thread, then list the messages
#         messages_response = create_run_and_list_messages(create_thread_run_request, openai_api_key=openai_api_key)
#         return messages_response
#     except Exception as e:
#         logging.error(f"Error in create_thread_and_run_endpoint: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

@router_runs.post("/create_thread_and_run", response_model=List[Dict[str, Any]])
async def create_thread_and_run_endpoint(
    create_thread_run_request: CreateThreadRunRequest,
    openai_api_key: str = Query(None, description="Optional OpenAI API key")
):
    try:
        logger.info(f"Received request for assistant_id: {create_thread_run_request.assistant_id}")
        logger.debug(f"Request body: {create_thread_run_request.json()}")

        if not create_thread_run_request.tools:
            create_thread_run_request.tools = [
                tool_class().get_definition() for tool_class in tool_registry.values()
            ]
            logger.info(f"Added {len(create_thread_run_request.tools)} tools to the request")

        request_dict = create_thread_run_request.dict()
        logger.debug(f"Converted request to dict: {request_dict}")

        messages_response = create_run_and_list_messages(request_dict, openai_api_key=openai_api_key)
        logger.info("Successfully created run and listed messages")
        
        if isinstance(messages_response, list):
            return messages_response
        elif isinstance(messages_response, dict) and 'data' in messages_response:
            return messages_response['data']
        else:
            raise ValueError("Unexpected response format from create_run_and_list_messages")

    except Exception as e:
        logger.exception(f"Error in create_thread_and_run_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router_runs.post("/run_thread_and_list_messages", response_model=Union[List[Dict[str, Any]], Dict[str, Any]])
async def run_thread_and_list_messages_endpoint(
    run_thread_request: RunThreadRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        logger.info(f"Received request to run thread {run_thread_request.thread_id} with assistant {run_thread_request.assistant_id}")
        
        messages_response = run_thread_and_list_messages(
            thread_id=run_thread_request.thread_id,
            assistant_id=run_thread_request.assistant_id,
            tools=run_thread_request.tools,
            openai_api_key=openai_api_key
        )
        return messages_response
    except Exception as e:
        logger.exception(f"Error in run_thread_and_list_messages_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")