from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class CreateAssistantRequest(BaseModel):
    model: str = "gpt-4o"
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    response_format: Optional[Any] = "auto" 

class ToolDefinition(BaseModel):
    type: str
    function: Dict[str, Any]

class CreateAssistantWithToolsRequest(BaseModel):
    model: str = "gpt-4o"
    name: Optional[str] = Field(None, description="The name of the assistant")
    description: Optional[str] = Field(None, description="The description of the assistant")
    instructions: Optional[str] = Field(None, description="The system instructions that the assistant uses")
    tools: List[ToolDefinition] = Field(default_factory=list, description="A list of tools enabled on the assistant")
    file_ids: Optional[List[str]] = Field(default_factory=list, description="A list of file IDs attached to the assistant")
    metadata: Optional[Dict[str, str]] = Field(None, description="Set of key-value pairs that can be attached to an object")
class Assistant(BaseModel):
    id: str
    object: str
    created_at: int
    name: Optional[str]
    description: Optional[str]
    model: str
    instructions: Optional[str]
    tools: List[Any] = []
    tool_resources: Optional[Dict[str, Any]] = None
    metadata: Dict[str, str] = {}
    temperature: Optional[float]
    top_p: Optional[float]
    response_format: Union[str, Dict[str, str], None] = "auto"

class ListAssistantsResponse(BaseModel):
    object: str
    data: List[Assistant]
    first_id: str
    last_id: str
    has_more: bool

class ModifyAssistantRequest(BaseModel):
    model: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[dict]] = []
    tool_resources: Optional[Dict[str, Union[dict, None]]] = None
    metadata: Optional[Dict[str, Union[str, int]]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, Dict[str, str]]] = "auto"
    
class DeleteAssistantResponse(BaseModel):
    id: str
    object: str
    deleted: bool
    
class UpdateAssistantRequest(BaseModel):
    assistant_id: str
    name: Optional[str] = None
    instructions: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[List[str]] = None