# Remove any imports like:
# from app.services.agent_services.direct_bridge import DirectAssistantBridge
# Remove any code that uses the DirectAssistantBridge class 

# Replace any code that might be choosing between bridges:
# bridge = DirectAssistantBridge(...) if use_direct_api else AssistantBridge(...)
# With:
bridge = AssistantBridge(...) 

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your existing services
from app.services.assistant_bridge import AssistantBridge
from app.services.workato_integration import WorkatoConfig
from services.service_db import DBService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard Workato configuration (you might want to load this from environment variables)
WORKATO_CONFIG = WorkatoConfig(
    api_token="ad19767e318455a1daa7635b3e5f3ce4055f11376155b45c506ceb4f4f739d1c",
    endpoint_url="https://apim.workato.com/solconsult/assistant-tools-v1/workato-root-tool"
)

# Create FastAPI app
app = FastAPI(title="OpenAI Agents WebSocket API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for connection parameters
class ConnectionParams(BaseModel):
    solomon_consumer_key: str
    assistant_id: str
    vector_store_ids: Optional[List[str]] = None
    thread_id: Optional[str] = None  # Add thread_id to support conversation persistence

# Store active connections and their associated thread IDs
active_connections: Dict[str, AssistantBridge] = {}
thread_connections: Dict[str, str] = {}  # Maps thread_ids to connection_ids

# Authentication dependency
async def get_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    # In production, you would validate the API key against your database
    return x_api_key

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with the assistant."""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    
    try:
        # Wait for connection parameters
        logger.info(f"New connection {connection_id} established, waiting for parameters")
        params_json = await websocket.receive_text()
        params = json.loads(params_json)
        
        # Validate required parameters
        if not params.get("solomon_consumer_key") or not params.get("assistant_id"):
            await websocket.send_json({
                "type": "error",
                "error": "Missing required parameters: solomon_consumer_key and assistant_id are required"
            })
            await websocket.close()
            return
        
        # Initialize the assistant bridge
        logger.info(f"Initializing AssistantBridge for connection {connection_id}")
        solomon_consumer_key = params.get("solomon_consumer_key")
        assistant_id = params.get("assistant_id")
        vector_store_ids = params.get("vector_store_ids")

        # Retrieve OpenAI API key using DBService
        openai_api_key = await DBService.get_openai_api_key(solomon_consumer_key)
        if not openai_api_key:
            await websocket.send_json({
                "type": "error",
                "error": "Invalid Solomon Consumer Key"
            })
            await websocket.close()
            return
        thread_id = params.get("thread_id")  # Get thread_id if provided

        try:
            bridge = AssistantBridge(
                api_key=openai_api_key,
                assistant_id=assistant_id,
                vector_store_ids=vector_store_ids
            )
            await bridge.initialize(workato_config=WORKATO_CONFIG)
            
            # If thread_id is provided, restore the conversation state
            if thread_id:
                bridge.session_memory.set_thread_id(thread_id)
                # Load any existing conversation history for this thread
                # (assuming you have implemented this in your storage layer)
            else:
                # Generate new thread_id for new conversations
                thread_id = str(uuid.uuid4())
                bridge.session_memory.set_thread_id(thread_id)
            
            # Store the bridge instance and thread mapping
            active_connections[connection_id] = bridge
            thread_connections[thread_id] = connection_id
            
            # Notify client that the assistant is ready
            await websocket.send_json({
                "type": "ready",
                "message": "Assistant initialized successfully",
                "thread_id": thread_id
            })
            
            # Process messages
            while True:
                # Wait for a message from the client
                message_json = await websocket.receive_text()
                message_data = json.loads(message_json)
                
                # Process commands
                if message_data.get("type") == "command":
                    command = message_data.get("command")
                    
                    if command == "clear_history":
                        bridge.clear_history()
                        await websocket.send_json({
                            "type": "system",
                            "message": "Conversation history cleared"
                        })
                        continue

                    elif command == "get_history":
                        history = bridge.get_conversation_history()
                        await websocket.send_json({
                            "type": "history",
                            "history": history
                        })
                        continue

                # Process chat messages
                if message_data.get("type") == "message":
                    user_input = message_data.get("content", "")
                    if not user_input.strip():
                        continue

                    # Send acknowledgment
                    await websocket.send_json({
                        "type": "system",
                        "message": "Processing your message..."
                    })

                    # Handle streaming response
                    if message_data.get("stream", True):
                        try:
                            # Send response in chunks
                            tool_used = False
                            full_response = ""

                            async for chunk, event_type in bridge.chat_streaming(user_input):
                                if event_type == "raw_response" or event_type == "message":
                                    # Text content
                                    await websocket.send_json({
                                        "type": "stream",
                                        "content": chunk,
                                        "event_type": event_type
                                    })
                                    full_response += chunk
                                elif event_type == "tool_call":
                                    # Tool call event
                                    tool_used = True
                                    await websocket.send_json({
                                        "type": "tool",
                                        "tool": "call",
                                        "name": chunk
                                    })
                                elif event_type == "tool_output":
                                    # Tool output event
                                    await websocket.send_json({
                                        "type": "tool",
                                        "tool": "output",
                                        "content": chunk
                                    })

                            # Send completion message
                            await websocket.send_json({
                                "type": "completion",
                                "content": full_response,
                                "tool_used": tool_used,
                                "thread_id": thread_id
                            })

                        except Exception as e:
                            logger.error(f"Error during streaming: {str(e)}")
                            await websocket.send_json({
                                "type": "error",
                                "error": f"Error during response streaming: {str(e)}"
                            })
                    else:
                        # Handle non-streaming response
                        try:
                            response = await bridge.chat(user_input)
                            await websocket.send_json({
                                "type": "response",
                                "content": response,
                                "thread_id": thread_id
                            })
                        except Exception as e:
                            logger.error(f"Error during chat: {str(e)}")
                            await websocket.send_json({
                                "type": "error",
                                "error": f"Error processing message: {str(e)}"
                            })

        except Exception as e:
            logger.error(f"Error initializing bridge: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "error": f"Error initializing assistant: {str(e)}"
            })
            await websocket.close()
            return

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"Error in websocket connection: {str(e)}")
    finally:
        # Clean up connection
        if connection_id in active_connections:
            bridge = active_connections[connection_id]
            thread_id = bridge.session_memory.get_thread_id()
            if thread_id:
                thread_connections.pop(thread_id, None)
            active_connections.pop(connection_id)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    active_connections.clear()
    thread_connections.clear()
