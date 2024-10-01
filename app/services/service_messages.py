import aiohttp
import logging
from models.models_messages import ListMessagesResponse, CreateMessageRequest, CreateMessageResponse
import os
from typing import Optional
from utils import get_headers

logger = logging.getLogger(__name__)

async def list_thread_messages(thread_id: str, limit: int = 20, order: str = "desc", openai_api_key: Optional[str] = None) -> ListMessagesResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = get_headers(openai_api_key)
    params = {
        "limit": limit,
        "order": order
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                response_json = await response.json()
                return ListMessagesResponse(**response_json)
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP Error: {e}, Response Content: {await response.text()}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Request Error: {e}")
            raise

async def create_message(thread_id: str, create_message_request: CreateMessageRequest, openai_api_key: Optional[str] = None) -> CreateMessageResponse:
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = get_headers(openai_api_key)
    payload = create_message_request.dict(exclude_unset=True)  # This excludes None values and unset fields
    
    logger.info(f"Sending request to {url}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Payload: {payload}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                response_json = await response.json()
                return CreateMessageResponse(**response_json)
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP Error: {e}, Response Content: {await response.text()}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Request Error: {e}")
            raise