from typing import List, Optional, Dict
from pydantic import BaseModel

class CreateVectorStoreRequest(BaseModel):
    file_ids: Optional[List[str]] = None
    name: Optional[str] = None
    expires_after: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, str]] = None

class FileCounts(BaseModel):
    in_progress: int
    completed: int
    failed: int
    cancelled: int
    total: int

class VectorStoreResponse(BaseModel):
    id: str
    object: str
    created_at: int
    name: Optional[str] = None
    usage_bytes: Optional[int] = None
    status: str
    expires_at: Optional[int] = None
    last_active_at: Optional[int] = None
    file_counts: FileCounts
    metadata: Optional[Dict[str, str]] = None

class ListVectorStoresResponse(BaseModel):
    object: str
    data: List[VectorStoreResponse]
    first_id: Optional[str] = None
    last_id: Optional[str] = None
    has_more: bool

class DeleteVectorStoreResponse(BaseModel):
    id: str
    object: str
    deleted: bool