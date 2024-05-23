from pydantic import BaseModel
from typing import Optional
from typing import List

class UploadFileRequest(BaseModel):
    purpose: str
    
class UploadFileRequest(BaseModel):
    file: str  # Assuming the file is a string representation or path
    purpose: Optional[str] = "assistants"

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