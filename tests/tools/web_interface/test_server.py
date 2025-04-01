"""
Test server for the web interface to test the OpenAI Assistant Bridge.
This is separate from the main application to keep the backend clean.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
import json
from typing import List, Dict, Any

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
        self.active_connections: List[WebSocket] = []
        self.agent_services = {}  # Store agent services by connection
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.agent_services:
                del self.agent_services[websocket]
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
        
    async def send_json(self, data: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(data)

# Initialize the connection manager
manager = ConnectionManager()

@test_app.get("/")
async def read_root():
    """Serve the test interface HTML page"""
    return FileResponse(str(static_dir / "index.html"))

@test_app.websocket("/ws/assistant/{assistant_id}")
async def websocket_endpoint(websocket: WebSocket, assistant_id: str):
    await manager.connect(websocket)
    try:
        await manager.send_json({
            "type": "connection_established",
            "data": {
                "assistant_id": assistant_id,
                "message": "Connected to the test interface"
            }
        }, websocket)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "initialize":
                # Initialize agent service
                from app.services.agent_service import AgentService
                
                api_key = data.get("api_key")
                vector_store_ids = data.get("vector_store_ids", [])
                
                if not api_key:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "API key is required for initialization"}
                    }, websocket)
                    continue
                
                try:
                    # Initialize agent service
                    agent_service = AgentService(api_key=api_key)
                    await agent_service.initialize(
                        assistant_id=assistant_id,
                        vector_store_ids=vector_store_ids
                    )
                    
                    # Store the agent service for this connection
                    manager.agent_services[websocket] = agent_service
                    
                    await manager.send_json({
                        "type": "initialized",
                        "data": {"message": "Agent service initialized successfully"}
                    }, websocket)
                    
                except Exception as e:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": f"Initialization error: {str(e)}"}
                    }, websocket)
            
            elif data.get("type") == "chat_message":
                # Process chat message using the agent service
                message = data.get("message", "")
                if not message:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": "Message content is required"}
                    }, websocket)
                    continue
                
                try:
                    agent_service = manager.agent_services.get(websocket)
                    if not agent_service:
                        await manager.send_json({
                            "type": "error",
                            "data": {"message": "Agent service not initialized"}
                        }, websocket)
                        continue
                    
                    async for event in agent_service.run_existing_agent_streaming(message):
                        if event.type == "stream":
                            await manager.send_json({
                                "type": "stream",
                                "content": event.data.get("content", "")
                            }, websocket)
                        elif event.type == "tool":
                            await manager.send_json({
                                "type": "tool",
                                "tool": event.data.get("tool"),
                                "name": event.data.get("name"),
                                "content": event.data.get("content")
                            }, websocket)
                        elif event.type == "system":
                            await manager.send_json({
                                "type": "system",
                                "message": event.data.get("message")
                            }, websocket)
                        
                except Exception as e:
                    await manager.send_json({
                        "type": "error",
                        "data": {"message": f"Error processing message: {str(e)}"}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(test_app, host="0.0.0.0", port=8081)  # Note: Using different port for test interface 