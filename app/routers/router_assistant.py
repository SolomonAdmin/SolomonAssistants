from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Path
from models.models_assistants import CreateAssistantRequest, ListAssistantsResponse, Assistant, ModifyAssistantRequest, DeleteAssistantResponse, CreateAssistantWithToolsRequest
from services.service_assistants import create_assistant_service, list_openai_assistants, modify_openai_assistant, delete_openai_assistant, create_assistant_with_tools
import logging
from typing import Optional
from tools import tool_registry


router_assistant = APIRouter(prefix="/assistant", tags=["Assistants V2"])

@router_assistant.post("/create_with_tools", response_model=Assistant)
async def create_assistant_with_tools_endpoint(
    assistant_data: CreateAssistantWithToolsRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        if not assistant_data.tools:
            assistant_data.tools = [
                tool_class().get_definition() for tool_class in tool_registry.values()
            ]
        
        assistant = create_assistant_with_tools(assistant_data, openai_api_key)
        return assistant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {str(e)}")

@router_assistant.post("/create_assistant")
async def create_assistant(
    assistant: CreateAssistantRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
    ):
    try:
        response = await create_assistant_service(assistant, openai_api_key)
        return response
    except Exception as e:
        logging.error(f"Error in create_assistant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_assistant.get("/list_assistants", response_model=ListAssistantsResponse)
async def get_openai_assistants_endpoint(
    order: str = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    limit: int = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20."),
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        response = list_openai_assistants(order=order, limit=limit, openai_api_key=openai_api_key) 
        return response
    except Exception as e:
        logging.error(f"Error in get_openai_assistants endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_assistant.post("/modify_assistant/{assistant_id}", response_model=Assistant)
async def modify_assistant(
    assistant_id: str,
    request: ModifyAssistantRequest,
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        response = modify_openai_assistant(assistant_id, request.dict(exclude_unset=True), openai_api_key=openai_api_key)
        return response
    except Exception as e:
        logging.error(f"Error in modify_assistant endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router_assistant.delete("/delete_assistant/{assistant_id}", response_model=DeleteAssistantResponse)
async def delete_assistant(
    assistant_id: str = Path(..., description="The ID of the assistant to delete"),
    openai_api_key: Optional[str] = Query(None, description="Optional OpenAI API key")
):
    try:
        response = delete_openai_assistant(assistant_id, openai_api_key=openai_api_key)
        return response
    except Exception as e:
        logging.error(f"Error in delete_assistant endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")