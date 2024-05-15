from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class AssistantData(BaseModel):
    model: str = "gpt-4-1106-preview"
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[str]] = [{"type": "file_search"}]
    file_ids: Optional[List[str]] = []
    metadata: Optional[Dict[str, str]] = {}

class ModifyAssistantRequest(BaseModel):
    name: Optional[str] = None
    description: str = ""
    instructions: str = ""
    tools: List[str] = []
    model: str = "gpt-4-1106-preview"
    file_ids: List[str] = []
    metadata: Optional[Dict[str, str]] = None

class ThreadUpdateRequest(BaseModel):
    metadata: Dict[str, str] = Field(
        default={},
        description="Set of key-value pairs for metadata. Keys can be a maximum of 64 characters long and values can be a maximum of 512 characters long."
    )
