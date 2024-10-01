from fastapi import HTTPException
import requests
import logging
from models.models_runs import CreateThreadRunRequest, RunResponse
from models.models_messages import ListMessagesResponse
from services.service_messages import list_thread_messages
import os
import time
from utils import get_headers
from tools import tool_registry
import json
from typing import List, Dict, Any, Union, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger = logging.getLogger(__name__)

def create_and_run_thread(create_thread_run_request: CreateThreadRunRequest, openai_api_key: str = None) -> RunResponse:
    url = "https://api.openai.com/v1/threads/runs"
    headers = get_headers(openai_api_key)

    thread_payload = {
        "assistant_id": create_thread_run_request.assistant_id,
        "thread": create_thread_run_request.thread.dict()
    }

    try:
        response = requests.post(url, headers=headers, json=thread_payload)
        response.raise_for_status()
        return RunResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise

def run_thread(thread_id: str, assistant_id: str, openai_api_key: str = None) -> RunResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = get_headers(openai_api_key)
    payload = {
        "assistant_id": assistant_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return RunResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise

def get_run_status(thread_id: str, run_id: str, openai_api_key: str = None) -> RunResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = get_headers(openai_api_key)

    logging.debug(f"Headers: {headers}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return RunResponse(**response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Request Error: {err}")
        raise

def poll_run_status(thread_id: str, run_id: str, openai_api_key: str = None, interval: int = 5, timeout: int = 300) -> RunResponse:
    start_time = time.time()
    while True:
        run_response = get_run_status(thread_id, run_id, openai_api_key)
        if run_response.status == "completed":
            return run_response
        elif time.time() - start_time > timeout:
            raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")
        time.sleep(interval)

def get_thread_messages(thread_id: str, limit: int = 20, order: str = "desc", openai_api_key: str = None) -> ListMessagesResponse:
    return list_thread_messages(thread_id, limit, order, openai_api_key)

# def create_run_and_list_messages(create_thread_run_request: CreateThreadRunRequest, openai_api_key: str = None, interval: int = 5, timeout: int = 300) -> ListMessagesResponse:
#     # Create and run the thread
#     initial_response = create_and_run_thread(create_thread_run_request, openai_api_key)
    
#     # Poll the run status until it is completed
#     final_response = poll_run_status(initial_response.thread_id, initial_response.id, openai_api_key, interval, timeout)
    
#     # List the messages in the completed thread
#     return get_thread_messages(final_response.thread_id, openai_api_key=openai_api_key)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_request(url, method='get', **kwargs):
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response

def run_thread_and_list_messages(
    thread_id: str, 
    assistant_id: str, 
    tools: Optional[List[Dict[str, Any]]] = None,
    openai_api_key: str = None, 
    interval: int = 5, 
    timeout: int = 300
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    headers = get_headers(openai_api_key)
    
    logger.info(f"Running thread {thread_id} with assistant {assistant_id}")
    run_url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    run_payload = {"assistant_id": assistant_id}
    
    if tools:
        run_payload['tools'] = tools
        logger.info(f"Added {len(tools)} tools to run payload")
    
    try:
        run_response = make_request(run_url, method='post', headers=headers, json=run_payload)
        run = run_response.json()
        logger.info(f"Run created with ID: {run['id']}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create run: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create run")
    
    start_time = time.time()
    
    logger.info("Waiting for run to complete")
    while run['status'] not in ['completed', 'failed', 'cancelled']:
        if time.time() - start_time > timeout:
            logger.error(f"Run timed out after {timeout} seconds")
            raise HTTPException(status_code=504, detail="Run timed out")
        
        time.sleep(interval)
        run_status_url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run['id']}"
        try:
            run_status_response = make_request(run_status_url, headers=headers)
            run = run_status_response.json()
            logger.info(f"Current run status: {run['status']}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get run status: {str(e)}")
            continue
        
        if run['status'] == 'requires_action':
            logger.info("Run requires action, handling tools")
            run = handle_run_with_tools(run, thread_id, openai_api_key)
    
    logger.info(f"Run completed with status: {run['status']}")

    logger.info("Listing messages")
    messages_url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    try:
        messages_response = make_request(messages_url, headers=headers)
        messages = messages_response.json()
        logger.info(f"Retrieved messages")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve messages")
    
    if 'data' in messages and isinstance(messages['data'], list):
        return messages['data']
    elif isinstance(messages, dict):
        return messages
    else:
        logger.error(f"Unexpected message format: {messages}")
        raise HTTPException(status_code=500, detail="Unexpected message format from OpenAI API")
    
def execute_tool(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = tool_call['function']['name']
    arguments = json.loads(tool_call['function']['arguments'])
    
    logger.info(f"Executing tool: {tool_name}")
    logger.debug(f"Tool arguments: {arguments}")

    tool_class = tool_registry.get(tool_name)
    if not tool_class:
        logger.error(f"Unknown tool: {tool_name}")
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool = tool_class()
    result = tool.execute(**arguments)
    
    logger.info(f"Tool {tool_name} execution completed")
    
    # If result is already a string, use it directly
    if isinstance(result, str):
        output = result
    else:
        # If it's not a string, try to serialize it to JSON
        try:
            output = json.dumps(result)
        except TypeError:
            # If serialization fails, convert to string
            output = str(result)

    logger.debug(f"Tool result: {output}")

    return {
        "tool_call_id": tool_call['id'],
        "output": output
    }

def handle_run_with_tools(run: Dict[str, Any], thread_id: str, openai_api_key: str) -> Dict[str, Any]:
    headers = get_headers(openai_api_key)
    while run['status'] == 'requires_action':
        logger.info(f"Run {run['id']} requires action")
        tool_calls = run['required_action']['submit_tool_outputs']['tool_calls']
        logger.debug(f"Tool calls: {tool_calls}")

        tool_outputs = [execute_tool(tool_call) for tool_call in tool_calls]
        logger.info(f"Executed {len(tool_outputs)} tools")
        
        url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run['id']}/submit_tool_outputs"
        response = requests.post(url, headers=headers, json={"tool_outputs": tool_outputs})
        response.raise_for_status()
        run = response.json()
        logger.info(f"Submitted tool outputs, new run status: {run['status']}")
    
    return run

def create_run_and_list_messages(create_thread_run_request: Dict[str, Any], openai_api_key: str = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    # Log the API key (partially masked)
    if openai_api_key:
        logger.info(f"Using OpenAI API key: {openai_api_key}")
    else:
        logger.warning("No OpenAI API key provided")

    headers = get_headers(openai_api_key)
    
    logger.info("Creating thread")
    thread_url = "https://api.openai.com/v1/threads"
    thread_payload = {"messages": create_thread_run_request['thread']['messages']}
    thread_response = requests.post(thread_url, headers=headers, json=thread_payload)
    try:
        thread_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error when creating thread: {e}")
        logger.error(f"Response content: {thread_response.text}")
        raise

    thread_id = thread_response.json()['id']
    logger.info(f"Thread created with ID: {thread_id}")

    logger.info("Creating run")
    run_url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    run_payload = {
        "assistant_id": create_thread_run_request['assistant_id'],
        "instructions": create_thread_run_request.get('instructions')
    }
    
    if 'tools' in create_thread_run_request:
        run_payload['tools'] = create_thread_run_request['tools']
        logger.info(f"Added {len(create_thread_run_request['tools'])} tools to run payload")
    
    logger.debug(f"Run payload: {run_payload}")
    run_response = requests.post(run_url, headers=headers, json=run_payload)
    try:
        run_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error when creating run: {e}")
        logger.error(f"Response content: {run_response.text}")
        raise

    run = run_response.json()
    logger.info(f"Run created with ID: {run['id']}")
    
    start_time = time.time()
    timeout = 600  # 10 minutes timeout
    
    logger.info("Waiting for run to complete")
    while run['status'] not in ['completed', 'failed', 'cancelled']:
        if time.time() - start_time > timeout:
            logger.error(f"Run timed out after {timeout} seconds")
            raise HTTPException(status_code=504, detail="Run timed out")
        
        time.sleep(5)
        run_status_url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run['id']}"
        run_status_response = requests.get(run_status_url, headers=headers)
        try:
            run_status_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error when checking run status: {e}")
            logger.error(f"Response content: {run_status_response.text}")
            raise

        run = run_status_response.json()
        logger.info(f"Current run status: {run['status']}")
        
        if run['status'] == 'requires_action':
            logger.info("Run requires action, handling tools")
            run = handle_run_with_tools(run, thread_id, openai_api_key)
    
    logger.info(f"Run completed with status: {run['status']}")

    logger.info("Listing messages")
    messages_url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    messages_response = requests.get(messages_url, headers=headers)
    try:
        messages_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error when listing messages: {e}")
        logger.error(f"Response content: {messages_response.text}")
        raise

    messages = messages_response.json()
    logger.info(f"Retrieved messages")
    
    # Check if 'data' key exists in the response
    if 'data' in messages and isinstance(messages['data'], list):
        return messages['data']
    elif isinstance(messages, dict):
        return messages
    else:
        logger.error(f"Unexpected message format: {messages}")
        raise HTTPException(status_code=500, detail="Unexpected message format from OpenAI API")