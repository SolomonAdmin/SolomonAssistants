from pydantic import BaseModel
from typing import Optional, List

class UploadFileRequest(BaseModel):
    purpose: str = "assistants"  # Default value set to "assistants"

class FileResponse(BaseModel):
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str

class UploadFileResponse(BaseModel):
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str

class ListFilesResponse(BaseModel):
    data: List[UploadFileResponse]
    object: str
