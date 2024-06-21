import requests
import logging
from models.models_runs import CreateThreadRunRequest, RunResponse
from models.models_messages import ListMessagesResponse
from services.service_messages import list_thread_messages
import os
import time
from utils import get_headers

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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

def create_run_and_list_messages(create_thread_run_request: CreateThreadRunRequest, openai_api_key: str = None, interval: int = 5, timeout: int = 300) -> ListMessagesResponse:
    # Create and run the thread
    initial_response = create_and_run_thread(create_thread_run_request, openai_api_key)
    
    # Poll the run status until it is completed
    final_response = poll_run_status(initial_response.thread_id, initial_response.id, openai_api_key, interval, timeout)
    
    # List the messages in the completed thread
    return get_thread_messages(final_response.thread_id, openai_api_key=openai_api_key)

def run_thread_and_list_messages(thread_id: str, assistant_id: str, openai_api_key: str = None, interval: int = 5, timeout: int = 300) -> ListMessagesResponse:
    # Run the thread
    initial_response = run_thread(thread_id, assistant_id, openai_api_key)
    
    # Poll the run status until it is completed
    final_response = poll_run_status(thread_id, initial_response.id, openai_api_key, interval, timeout)
    
    # List the messages in the completed thread
    return get_thread_messages(thread_id, openai_api_key=openai_api_key)
