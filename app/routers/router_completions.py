import os
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

# Simple in-memory session store
_SESSION_STORE: Dict[str, List[Dict[str, Any]]] = {}

router_completions = APIRouter(prefix="/api/v3/agent", tags=["Agent V3"])


class CompletionRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Used to track conversation memory")
    prompt: str = Field(..., description="The user's message")
    model: str = Field("gpt-4o", description="Model to use")
    system_message: Optional[str] = Field(None, description="Assistant persona")
    messages: Optional[List[Dict[str, Any]]] = Field(None, description="Previous messages")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tool/function schemas")
    tool_choice: Optional[str] = Field(None, description="Tool selection strategy")


class CompletionResponse(BaseModel):
    reply: str
    tool_calls: Optional[List[Dict[str, Any]]]
    messages: List[Dict[str, Any]]


openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router_completions.post("/request", response_model=CompletionResponse)
async def agent_request(req: CompletionRequest) -> CompletionResponse:
    try:
        # Load prior messages
        messages: List[Dict[str, Any]] = []
        if req.session_id and req.session_id in _SESSION_STORE:
            messages = list(_SESSION_STORE[req.session_id])
        elif req.messages:
            messages = list(req.messages)

        # Prepend system message if provided
        if req.system_message:
            messages.insert(0, {"role": "system", "content": req.system_message})

        # Append current user prompt
        messages.append({"role": "user", "content": req.prompt})

        # Generate response using OpenAI chat completions
        resp = await openai_client.chat.completions.create(
            model=req.model,
            messages=messages,
            tools=req.tools,
            tool_choice=req.tool_choice,
        )
        assistant_message = resp.choices[0].message
        reply_content = assistant_message.content or ""
        tool_calls = getattr(assistant_message, "tool_calls", None)

        # Append assistant response
        if hasattr(assistant_message, "model_dump"):
            messages.append(assistant_message.model_dump())
        elif hasattr(assistant_message, "dict"):
            messages.append(assistant_message.dict())
        else:
            messages.append({"role": "assistant", "content": reply_content, "tool_calls": tool_calls})

        # Save updated messages back to session
        if req.session_id:
            _SESSION_STORE[req.session_id] = messages

        return CompletionResponse(reply=reply_content, tool_calls=tool_calls, messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
