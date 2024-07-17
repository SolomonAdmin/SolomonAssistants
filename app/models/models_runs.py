from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str = "user"
    content: str

class Thread(BaseModel):
    messages: List[Message]

# class CreateThreadRunRequest(BaseModel):
#     assistant_id: str
#     thread: Thread

class Tool(BaseModel):
    type: str

class TruncationStrategy(BaseModel):
    type: str
    last_messages: Optional[Any]

class Usage(BaseModel):
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]

class RunResponse(BaseModel):
    id: str
    object: str
    created_at: int
    assistant_id: str
    thread_id: str
    status: str
    required_action: Optional[Any]
    last_error: Optional[Any]
    expires_at: Optional[int]
    started_at: Optional[int]
    cancelled_at: Optional[int]
    failed_at: Optional[int]
    completed_at: Optional[int]
    incomplete_details: Optional[Any]
    model: str
    instructions: Optional[str]
    tools: List[Tool]
    metadata: Dict[str, Any]
    usage: Optional[Usage]
    temperature: Optional[float]
    top_p: Optional[float]
    max_prompt_tokens: Optional[int]
    max_completion_tokens: Optional[int]
    truncation_strategy: Optional[TruncationStrategy]
    response_format: Optional[str]
    tool_choice: Optional[Any]

class ToolDefinition(BaseModel):
    type: str
    function: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict):
            return cls(**v)
        return v

class CreateThreadRunRequest(BaseModel):
    assistant_id: str
    thread: Thread
    tools: Optional[List[dict]] = None

class RunThreadRequest(BaseModel):
    thread_id: str
    assistant_id: str
    tools: Optional[List[Dict[str, Any]]] = None