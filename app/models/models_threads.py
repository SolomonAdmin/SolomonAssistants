from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class Thread(BaseModel):
    thread_id: str
    thread_name: Optional[str] = None

class ThreadsResponse(BaseModel):
    threads: list[Thread]

class CreateThreadRequest(BaseModel):
    messages: Optional[list] = None
    tool_resources: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ThreadResponse(BaseModel):
    id: str
    object: str
    created_at: int
    metadata: Dict[str, Any]
    tool_resources: Dict[str, Any]