from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Path, Header
from fastapi.params import Body
from fastapi.responses import JSONResponse
from models.models_assistants import CreateAssistantRequest, AssistantResponse, ListAssistantsRequest, ListAssistantsResponse, Assistant, ModifyAssistantRequest, DeleteAssistantResponse, CreateAssistantWithToolsRequest
from models.models_assistants import (
    CreateAssistantRequest, 
    ListAssistantsRequest, 
    ListAssistantsResponse, 
    ModifyAssistantRequest, 
    DeleteAssistantResponse,
    CreateAssistantWithToolsRequest,
    AssistantResponse,
)
from services.service_db import DBService
from services.service_assistants import create_assistant_service, list_openai_assistants, modify_openai_assistant, delete_openai_assistant, create_assistant_with_tools, get_openai_assistant
import logging
from typing import Optional
from tools import tool_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router_assistant = APIRouter(prefix="/assistant", tags=["Assistants V2"])

@router_assistant.post("/create_with_tools", response_model=Assistant, operation_id="create_assistant_with_tools")
async def create_assistant_with_tools_endpoint(
    assistant_data: CreateAssistantWithToolsRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        if not assistant_data.tools:
            assistant_data.tools = [
                tool_class().get_definition() for tool_class in tool_registry.values()
            ]
        
        assistant = create_assistant_with_tools(assistant_data, openai_api_key)
        return assistant
    except Exception as e:
        logging.error(f"Error in create_assistant_with_tools_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {str(e)}")
    
@router_assistant.post("/create_assistant", operation_id="create_assistant", response_model=AssistantResponse)
async def create_assistant(
    assistant: CreateAssistantRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = create_assistant_service(assistant, openai_api_key)
        return AssistantResponse(**response)  
    except Exception as e:
        logging.error(f"Error in create_assistant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_assistant.get("/list_assistants", response_model=ListAssistantsResponse, operation_id="list_assistants")
async def get_openai_assistants_endpoint(
    limit: Optional[int] = Query(20, description="A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20."),
    order: Optional[str] = Query("desc", description="Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order."),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = list_openai_assistants(
            limit=limit,
            order=order,
            openai_api_key=openai_api_key
        )
        
        return ListAssistantsResponse(**response)
    except Exception as e:
        logging.error(f"Error in get_openai_assistants endpoint: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    
@router_assistant.post("/modify_assistant/{assistant_id}", response_model=AssistantResponse)  # Keep as POST
async def modify_assistant(
    assistant_id: str = Path(..., description="The ID of the assistant to modify"),
    request: ModifyAssistantRequest = Body(..., description="The modifications to apply to the assistant"),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
) -> AssistantResponse:
    """
    Modify an existing assistant.
    """
    try:
        # Get OpenAI API key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        # Convert request to dict, maintaining the exact structure OpenAI expects
        modifications = request.dict(exclude_unset=True, exclude_none=True)
        
        logger.info(f"Modifying assistant {assistant_id}")
        logger.debug(f"Modification request: {modifications}")
        
        # Modify the assistant
        response = modify_openai_assistant(
            assistant_id=assistant_id,
            data=modifications,
            openai_api_key=openai_api_key
        )

        return AssistantResponse(**response)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in modify_assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router_assistant.delete("/delete_assistant/{assistant_id}", response_model=DeleteAssistantResponse, operation_id="delete_assistant")
async def delete_assistant(
    assistant_id: str = Path(..., description="The ID of the assistant to delete"),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = delete_openai_assistant(assistant_id, openai_api_key=openai_api_key)
        return DeleteAssistantResponse(**response)
    except Exception as e:
        logging.error(f"Error in delete_assistant endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router_assistant.get("/{assistant_id}", response_model=AssistantResponse, operation_id="get_assistant")
async def get_assistant(
    assistant_id: str = Path(..., description="The ID of the assistant to retrieve"),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication")
):
    try:
        # Retrieve the OpenAI API key using the solomon_consumer_key
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="Invalid Solomon Consumer Key")

        response = get_openai_assistant(assistant_id, openai_api_key=openai_api_key)
        return AssistantResponse(**response)
    except Exception as e:
        logging.error(f"Error in get_assistant endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")