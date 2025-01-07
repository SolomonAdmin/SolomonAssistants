from fastapi import APIRouter, Header, HTTPException
import requests
import logging
from models.models_workato import WorkatoAssistantBuilderRequest, WorkatoAssistantBuilderResponse

router_workato = APIRouter(prefix="/workato", tags=["Workato Integration"])

logger = logging.getLogger(__name__)

# Hardcoded API token - in production, consider moving this to environment variables or secure secrets management
WORKATO_API_TOKEN = "340a90abdecd4f0584569b180dc4c4326ebda649ca88e731dcaa44d04d30cbeb"
WORKATO_ENDPOINT = "https://apim.workato.com/solconsult/assistant-functions-v1/assistant-builder-functions"

@router_workato.post("/assistant-builder", response_model=WorkatoAssistantBuilderResponse)
async def forward_to_workato(
    request: WorkatoAssistantBuilderRequest,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    thread_id: str = Header(..., description="Thread ID for the request")
):
    try:
        # Prepare headers for Workato request
        headers = {
            "API-TOKEN": WORKATO_API_TOKEN,
            "Solomon_consumer_key": solomon_consumer_key,
            "Thread_id": thread_id,
            "Content-Type": "application/json"
        }

        # Prepare request body
        payload = {
            "name": request.name,
            "description": request.description,
            "instructions": request.instructions
        }

        # Forward request to Workato
        response = requests.post(
            WORKATO_ENDPOINT,
            headers=headers,
            json=payload
        )

        # Handle response
        if response.status_code == 200:
            return WorkatoAssistantBuilderResponse(
                success=True,
                message="Successfully forwarded request to Workato"
            )
        else:
            logger.error(f"Workato request failed: {response.text}")
            return WorkatoAssistantBuilderResponse(
                success=False,
                message=f"Workato request failed with status code: {response.status_code}"
            )

    except Exception as e:
        logger.error(f"Error forwarding request to Workato: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))