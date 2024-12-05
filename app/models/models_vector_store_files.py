from typing import Optional
from pydantic import BaseModel
from typing import List
from enum import Enum

class CreateVectorStoreFileRequest(BaseModel):
    file_id: str

class VectorStoreFileResponse(BaseModel):
    id: str
    object: str
    created_at: int
    usage_bytes: int
    vector_store_id: str
    status: str
    last_error: Optional[str] = None

class ListVectorStoreFilesResponse(BaseModel):
    object: str
    data: List[VectorStoreFileResponse]
    first_id: str
    last_id: str
    has_more: bool
    
class DeleteVectorStoreFileResponse(BaseModel):
    id: str
    object: str
    deleted: bool

class FileType(str, Enum):
    TXT = "txt"
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    PDF = "pdf"

class CreateVectorStoreFileWorkatoRequest(BaseModel):
    content: str
    file_name: str
    file_type: FileType