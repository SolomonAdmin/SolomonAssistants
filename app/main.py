import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from router import router
from routers.router_completions import router_completions
from routers.healthcheck import router_health_check
from fastapi.responses import Response
import yaml
import functools
import logging
from services.service_db import DBService

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Include routers
app.include_router(router_health_check)
app.include_router(router)
app.include_router(router_completions)

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
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    
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
        
        from app.services.assistant_bridge import AssistantBridge, StreamEvent
        
        # Maintain the bridge instance for this connection
        bridge = None
        
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "initialize":
                # Initialize the assistant bridge using Solomon Consumer Key
                solomon_consumer_key = data.get("solomon_consumer_key")
                vector_store_ids = data.get("vector_store_ids", [])

                if not solomon_consumer_key:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "Solomon Consumer Key is required for initialization"}
                    }, websocket)
                    continue

                # Fetch the OpenAI API key from the database
                openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
                if not openai_api_key:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "Invalid Solomon Consumer Key"}
                    }, websocket)
                    continue

                try:
                    bridge = AssistantBridge(
                        api_key=openai_api_key,
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
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await manager.send_json({
                "type": "error",
                "data": {"message": f"Unexpected error: {str(e)}"}
            }, websocket)
        except:
            pass
        manager.disconnect(websocket)

# Customize OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OpenAPI Assistants V2.0",
        version="0.1.0",
        description="REST API and WebSocket interface for OpenAI Assistants",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/openapi.yaml")
@functools.lru_cache()
def get_openapi_yaml() -> Response:
    openapi_json = app.openapi()  # Get the OpenAPI JSON spec
    yaml_output = yaml.dump(openapi_json)  # Convert JSON to YAML
    return Response(content=yaml_output, media_type="text/x-yaml")

# Debug middleware to log requests
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Received request: {request.method} {request.url}")
    print("Headers:")
    for name, value in request.headers.items():
        print(f"{name}: {value}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
