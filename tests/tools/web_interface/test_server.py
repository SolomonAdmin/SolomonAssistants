"""
Test server for the web interface to test the OpenAI Assistant Bridge.
This is separate from the main application to keep the backend clean.
"""
import sys
import os
import asyncio
import io
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

# Ensure project root (SolomonAssistants/) is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.services.agent_service import AgentService

try:
    # Import OpenAI Agents SDK voice pipeline components if available
    from agents.voice import SingleAgentVoiceWorkflow, VoicePipeline, AudioInput
    AGENTS_VOICE_AVAILABLE = True
except ImportError:
    AGENTS_VOICE_AVAILABLE = False
    print("Warning: OpenAI Agents SDK voice components not available.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize test server
test_app = FastAPI(title="Assistant Bridge Test Interface", version="0.1.0")

# Add CORS middleware
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Voice session instances
voice_sessions = {}

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

@test_app.post("/voice/start")
async def start_voice(request: Request):
    """Start a voice processing session"""
    # Parse request body
    data = await request.json()
    api_key = data.get("api_key")
    assistant_id = data.get("assistant_id")
    
    if not api_key or not assistant_id:
        return {"success": False, "error": "API key and assistant ID are required"}
    
    try:
        # Initialize agent service
        agent_service = AgentService(api_key=api_key)
        await agent_service.initialize(assistant_id)
        
        # Create a unique session ID
        session_id = f"{assistant_id}_{hash(api_key)}"
        
        # Store session info
        voice_sessions[session_id] = {
            "agent_service": agent_service,
            "assistant_id": assistant_id,
            "api_key": api_key
        }
        
        return {"success": True, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error initializing voice session: {str(e)}")
        return {"success": False, "error": str(e)}

@test_app.post("/voice/process")
async def process_voice(file: UploadFile = File(...), session_id: str = None):
    """Process audio input and return audio output"""
    if not session_id or session_id not in voice_sessions:
        return {"success": False, "error": "Invalid or expired session ID"}
    
    try:
        # Get the session
        session = voice_sessions[session_id]
        agent_service = session["agent_service"]
        api_key = session["api_key"]
        
        # Read audio data
        audio_data = await file.read()
        
        # Use OpenAI API directly for speech to text
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Create a temporary file for the audio data
        temp_audio_path = f"temp_audio_{session_id}.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        # Transcribe audio with Whisper API
        try:
            with open(temp_audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1"
                )
            text_input = transcription.text
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            text_input = ""
        finally:
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        
        if not text_input:
            return {"success": False, "error": "Could not transcribe audio"}
        
        # Process the text with the agent
        response_text = ""
        async for event in agent_service.run_existing_agent_streaming(text_input, {}):
            if event.type == "content_chunk":
                response_text += event.data.get("content", "")
        
        # Convert response text to speech using OpenAI TTS
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text
        )
        
        # Get the speech audio data
        speech_data = speech_response.content
        
        # Return the audio data as a streaming response
        return StreamingResponse(
            io.BytesIO(speech_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        return {"success": False, "error": str(e)}

@test_app.post("/voice/stop")
async def stop_voice(request: Request):
    """Stop a voice processing session"""
    data = await request.json()
    session_id = data.get("session_id")
    
    if not session_id or session_id not in voice_sessions:
        return {"success": False, "error": "Invalid or expired session ID"}
    
    try:
        # Remove the session
        del voice_sessions[session_id]
        return {"success": True}
    except Exception as e:
        logger.error(f"Error stopping voice session: {str(e)}")
        return {"success": False, "error": str(e)}

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
                    await agent_service.initialize(assistant_id, vector_store_ids=vector_store_ids)
                    logger.info(f"Agent service initialized with vector_store_ids: {vector_store_ids}")
                    
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
                    
                    # Send completion event when the response is finished
                    await websocket.send_json({
                        "type": "completion",
                        "data": {"message": "Processing completed"}
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