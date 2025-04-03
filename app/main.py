import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import logging
from app.router import router
from app.routers.healthcheck import router_health_check
import yaml
import functools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))

# Initialize the FastAPI application
app = FastAPI(title="OpenAPI Assistants V2.0", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the test interface
static_dir = Path(__file__).parent.parent / "tests" / "tools" / "web_interface" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Root endpoint to serve the test interface
@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
        
    async def send_json(self, data: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(data)

# Initialize the connection manager
manager = ConnectionManager()

# WebSocket endpoint for assistant chat
@app.websocket("/ws/assistant/{assistant_id}")
async def websocket_endpoint(websocket: WebSocket, assistant_id: str):
    await manager.connect(websocket)
    try:
        # Send welcome message
        await manager.send_json({
            "type": "connection_established",
            "data": {
                "assistant_id": assistant_id,
                "message": "Connected to the assistant service"
            }
        }, websocket)
        
        from app.services.assistant_bridge import AssistantBridge
        
        # Maintain the bridge instance for this connection
        bridge = None
        
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "initialize":
                # Initialize the assistant bridge
                api_key = data.get("api_key")
                vector_store_ids = data.get("vector_store_ids", [])
                
                if not api_key:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "API key is required for initialization"}
                    }, websocket)
                    continue
                
                try:
                    bridge = AssistantBridge(
                        api_key=api_key,
                        assistant_id=assistant_id,
                        vector_store_ids=vector_store_ids
                    )
                    await bridge.initialize()
                    
                    await manager.send_json({
                        "type": "initialized",
                        "data": {"message": "Assistant bridge initialized successfully"}
                    }, websocket)
                except Exception as e:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": f"Initialization error: {str(e)}"}
                    }, websocket)
            
            elif data.get("type") == "chat_message":
                # Process a chat message
                if not bridge:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "Bridge not initialized. Send an initialize message first."}
                    }, websocket)
                    continue
                
                message = data.get("message", "")
                if not message:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "Message content is required"}
                    }, websocket)
                    continue
                
                try:
                    # Use streaming mode for better real-time experience
                    await manager.send_json({
                        "type": "processing_started",
                        "data": {"message": "Processing your message..."}
                    }, websocket)
                    
                    async for event in bridge.chat_streaming(message):
                        content = event[0] if isinstance(event, tuple) else event.data.get("content", "")
                        event_type = event[1] if isinstance(event, tuple) else event.type
                        
                        if event_type == "tool_call" or event_type == "tool_event":
                            await manager.send_json({
                                "type": "tool_usage",
                                "data": {"message": content}
                            }, websocket)
                        elif event_type == "message" or event_type == "content_chunk":
                            await manager.send_json({
                                "type": "content_chunk",
                                "data": {"content": content}
                            }, websocket)
                    
                    await manager.send_json({
                        "type": "processing_complete",
                        "data": {"message": "Message processing complete"}
                    }, websocket)
                    
                except Exception as e:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": f"Error processing message: {str(e)}"}
                    }, websocket)
            
            elif data.get("type") == "clear_history":
                # Clear conversation history
                if bridge:
                    bridge.clear_history()
                    await manager.send_json({
                        "type": "history_cleared",
                        "data": {"message": "Conversation history cleared"}
                    }, websocket)
                else:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "Bridge not initialized"}
                    }, websocket)
                    
            else:
                await manager.send_json({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {data.get('type')}"}
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in websocket_endpoint: {str(e)}")
        manager.disconnect(websocket)

# Include routers
app.include_router(router_health_check)
app.include_router(router)