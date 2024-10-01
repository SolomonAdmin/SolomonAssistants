from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TextContent(BaseModel):
    value: str
    annotations: List[Any]

class Content(BaseModel):
    type: str
    text: TextContent

class IncompleteDetails(BaseModel):
    reason: str

class Message(BaseModel):
    id: str
    object: str
    created_at: int
    thread_id: str
    status: Optional[str] = None
    incomplete_details: Optional[IncompleteDetails] = None
    completed_at: Optional[int] = None
    incomplete_at: Optional[int] = None
    role: str
    content: List[Content]
    assistant_id: Optional[str] = None
    run_id: Optional[str] = None
    attachments: Optional[List[Any]] = None
    metadata: Dict[str, Any]

class ListMessagesResponse(BaseModel):
    object: str
    data: List[Message]
    first_id: Optional[str] = None
    last_id: Optional[str] = None
    has_more: bool

class CreateMessageRequest(BaseModel):
    role: str
    content: str
    attachments: Optional[List[Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class CreateMessageResponse(BaseModel):
    id: str
    object: str
    created_at: int
    thread_id: str
    role: str
    content: List[Content]
    attachments: Optional[List[Any]] = None
    metadata: Dict[str, Any]