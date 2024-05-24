from fastapi import APIRouter, HTTPException, Query
from models.models_messages import ListMessagesResponse
from services.service_messages import list_thread_messages
import logging

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