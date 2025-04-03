"""
Test server for the web interface to test the OpenAI Assistant Bridge.
This is separate from the main application to keep the backend clean.
"""
import sys
import os

# Ensure project root (SolomonAssistants/) is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
import json
from typing import List, Dict, Any
from app.services.agent_service import AgentService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize test server
test_app = FastAPI(title="Assistant Bridge Test Interface", version="0.1.0")

# Mount static files from the test interface directory
static_dir = Path(__file__).parent / "static"
test_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, AgentService] = {}
    
    async def connect(self, websocket: WebSocket, agent_service: AgentService):
        """Store the connection and agent service."""
        self.active_connections[websocket] = agent_service
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
    
    def get_agent_service(self, websocket: WebSocket) -> AgentService:
        """Get the agent service for a connection."""
        return self.active_connections.get(websocket)

# Initialize the connection manager
manager = ConnectionManager()

@test_app.get("/")
async def read_root():
    """Serve the connection page"""
    return FileResponse(str(static_dir / "index.html"))

@test_app.get("/static/{path:path}")
async def read_static(path: str):
    """Serve static files"""
    return FileResponse(str(static_dir / path))

@test_app.get("/chat")
async def read_chat():
    """Serve the chat interface page"""
    return FileResponse(str(static_dir / "chat.html"))

@test_app.websocket("/ws/assistant/{assistant_id}")
async def websocket_endpoint(websocket: WebSocket, assistant_id: str):
    try:
        await websocket.accept()
        logger.info("connection open")

        # Initialize agent service
        agent_service = None

        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data["type"] == "initialize":
                logger.info(f"Received init message: {data}")
                api_key = data["api_key"]
                vector_store_ids = data.get("vector_store_ids", [])
                
                try:
                    agent_service = AgentService(api_key=api_key)
                    await agent_service.initialize(assistant_id)
                    logger.info("Agent service initialized")
                    
                    await websocket.send_json({
                        "type": "initialized"
                    })
                    logger.info("Sent initialization success message")
                    
                except Exception as e:
                    error_msg = f"Failed to initialize agent: {str(e)}"
                    logger.error(error_msg)
                    await websocket.send_json({
                        "type": "error",
                        "error": error_msg
                    })
                    continue
            
            elif data["type"] == "chat_message":
                if not agent_service:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Agent not initialized"
                    })
                    continue
                
                try:
                    # Process message with streaming
                    logger.info("Starting streaming response")
                    
                    # Send initial system message
                    await websocket.send_json({
                        "type": "message",
                        "role": "system",
                        "content": "Starting agent processing"
                    })
                    
                    # Process the user message and stream the response
                    # Note: We don't echo back the user message since the client creates it
                    first_chunk = True  # Flag to mark the first chunk of this response
                    
                    async for event in agent_service.run_existing_agent_streaming(
                        input_text=data["message"],
                        context={}
                    ):
                        logger.info(f"Received event: {event}")
                        
                        if event.type == "content_chunk":
                            content = event.data.get("content", "")
                            if content.strip():  # Only send non-empty chunks
                                message_data = {
                                    "type": "message",
                                    "role": "assistant",
                                    "content": content
                                }
                                
                                # For the first chunk, add a flag to indicate a new turn
                                if first_chunk:
                                    message_data["new_turn"] = True
                                    first_chunk = False
                                    
                                await websocket.send_json(message_data)
                            
                        elif event.type == "tool_event":
                            # Send tool usage as system message
                            await websocket.send_json({
                                "type": "message",
                                "role": "system",
                                "content": f"Using tool: {event.data.get('name', 'unknown')}"
                            })
                            
                        elif event.type == "system":
                            # Send system message
                            await websocket.send_json({
                                "type": "message",
                                "role": "system",
                                "content": event.data.get("message", "")
                            })
                    
                    logger.info("Finished streaming response")
                            
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    await websocket.send_json({
                        "type": "message",
                        "role": "system",
                        "content": f"Error: {str(e)}"
                    })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(test_app, host="0.0.0.0", port=8081)  # Note: Using different port for test interface 