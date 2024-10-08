from fastapi import APIRouter, Depends, HTTPException
from models.models_threads import ThreadsResponse
from services.service_threads import ThreadService

router_threads = APIRouter(prefix="/thread", tags=["RDS"])

@router_threads.get("/threads/{solomon_consumer_key}", response_model=ThreadsResponse)
async def get_threads(solomon_consumer_key: str, thread_service: ThreadService = Depends(ThreadService)):
    threads = thread_service.get_threads(solomon_consumer_key)
    if not threads:
        raise HTTPException(status_code=404, detail="No threads found for the given consumer key")
    return ThreadsResponse(threads=threads)