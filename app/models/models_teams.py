from pydantic import BaseModel
from typing import Optional, List

class TeamMemberCreate(BaseModel):
    callable_assistant_id: str
    callable_assistant_reason: Optional[str] = None

class TeamCallableAssistant(BaseModel):
    callable_assistant_id: str
    callable_assistant_reason: Optional[str] = None

class TeamCallableAssistantsResponse(BaseModel):
    callable_assistants: List[TeamCallableAssistant]