from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class Tool(BaseModel):
    type: str = Field(..., description="The type of the tool")

class ToolResources(BaseModel):
    file_search: Optional[Dict[str, List[str]]] = Field(None, description="Resources for the file search tool")

# Create assistants models
class CreateAssistantRequest(BaseModel):
    model: str
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[Tool]] = None
    metadata: Optional[dict] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, dict]] = None

class AssistantResponse(BaseModel):
    id: str
    object: str = Field(..., description="The object type, which is always 'assistant'")
    created_at: int
    name: Optional[str] = None
    description: Optional[str] = None
    model: str
    instructions: Optional[str] = None
    tools: List[Tool]
    metadata: dict = Field(default_factory=dict)
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    response_format: Optional[Union[str, dict]] = None

# List assistants models
class Assistant(BaseModel):
    id: str
    object: str = Field("assistant", description="The object type, which is always 'assistant'")
    created_at: int
    name: Optional[str] = None
    description: Optional[str] = None
    model: str
    instructions: Optional[str] = None
    tools: List[Tool] = Field(default_factory=list)
    tool_resources: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    response_format: Optional[Union[str, dict]] = None

class ListAssistantsRequest(BaseModel):
    limit: Optional[int] = Field(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.")
    order: Optional[str] = Field("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.")
    after: Optional[str] = Field(None, description="A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.")
    before: Optional[str] = Field(None, description="A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.")

class ListAssistantsResponse(BaseModel):
    object: str = Field("list", description="The object type, which is always 'list'")
    data: List[Assistant]
    first_id: str
    last_id: str
    has_more: bool

# Modify assistant models
class ModifyAssistantRequest(BaseModel):
    model: Optional[str] = Field(None, description="ID of the model to use")
    name: Optional[str] = Field(None, description="The name of the assistant")
    description: Optional[str] = Field(None, description="The description of the assistant")
    instructions: Optional[str] = Field(None, description="The system instructions that the assistant uses")
    tools: Optional[List[Union[str, Dict[str, Any]]]] = None
    tool_resources: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Union[str, int]]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, Dict[str, str]]] = None

class AssistantResponse(BaseModel):
    id: str = Field(..., description="The ID of the assistant")
    object: str = Field("assistant", description="The object type, which is always 'assistant'")
    created_at: int = Field(..., description="The Unix timestamp (in seconds) for when the assistant was created")
    name: Optional[str] = Field(None, description="The name of the assistant")
    description: Optional[str] = Field(None, description="The description of the assistant")
    model: str = Field(..., description="ID of the model used by the assistant")
    instructions: Optional[str] = Field(None, description="The system instructions that the assistant uses")
    tools: List[Tool] = Field(default_factory=list, description="A list of tools enabled on the assistant")
    tool_resources: Optional[ToolResources] = Field(None, description="A set of resources that are used by the assistant's tools")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with the assistant")
    top_p: Optional[float] = Field(None, description="The top_p value used for nucleus sampling")
    temperature: Optional[float] = Field(None, description="The temperature used for sampling")
    response_format: Optional[Union[str, Dict[str, Any]]] = Field(None, description="The format of the response")

# Delete assistant models
class DeleteAssistantResponse(BaseModel):
    id: str = Field(..., description="The ID of the deleted assistant")
    object: str = Field(..., description="The object type, which is 'assistant.deleted'")
    deleted: bool = Field(..., description="Indicates whether the assistant was successfully deleted")

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

class ListAssistantsResponse(BaseModel):
    object: str
    data: List[Assistant]
    first_id: str
    last_id: str
    has_more: bool

# Modify assistants models
class ModifyAssistantRequest(BaseModel):
    model: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[Union[str, Dict[str, Any]]]] = None
    tool_resources: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Union[str, int]]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, Dict[str, str]]] = None
    
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