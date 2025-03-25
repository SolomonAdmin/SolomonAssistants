from typing import Dict, Any, List, Optional, AsyncGenerator, Union, Tuple
import logging
import json
import asyncio
from openai import AsyncOpenAI
from dataclasses import dataclass

# Import local modules
try:
    from .model_management import ModelManagementService
    from .tool_management import ToolManagementService
    from .agent_service import AgentService, StreamEvent as AgentStreamEvent
    from .workato_integration import WorkatoConfig, WorkatoIntegration
    AGENT_SERVICES_AVAILABLE = True
except ImportError:
    AGENT_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class StreamEvent:
    """Custom event class for streaming events."""
    type: str
    data: Dict[str, Any]

class AssistantBridgeError(Exception):
    """Base exception for assistant bridge errors."""
    pass

class AssistantBridge:
    def __init__(self, api_key: str, assistant_id: str, vector_store_ids: Optional[List[str]] = None):
        """
        Bridge between Assistant API and front-end.
        
        Args:
            api_key: OpenAI API key
            assistant_id: Existing Assistant ID to get configuration from
            vector_store_ids: Optional list of vector store IDs for file search
        """
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.vector_store_ids = vector_store_ids
        self.conversation_history = []
        self.openai_client = AsyncOpenAI(api_key=api_key)
        self._thread_id = None
        self.initialized = False
        
        # Initialize agent service if available
        if AGENT_SERVICES_AVAILABLE:
            self.agent_service = AgentService(api_key)
        else:
            self.agent_service = None
        
    async def initialize(self, workato_config=None):
        """Initialize the bridge."""
        try:
            # Fetch assistant data to verify it exists
            assistant = await self.openai_client.beta.assistants.retrieve(self.assistant_id)
            logger.info(f"Successfully connected to assistant: {assistant.name}")
            
            # Initialize agent service if available
            if AGENT_SERVICES_AVAILABLE and self.agent_service:
                await self.agent_service.initialize(
                    assistant_id=self.assistant_id,
                    vector_store_ids=self.vector_store_ids,
                    workato_integration=WorkatoIntegration(workato_config) if workato_config else None
                )
            
            # Create a new thread
            thread = await self.openai_client.beta.threads.create()
            self._thread_id = thread.id
            logger.info(f"Created thread: {thread.id}")
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize assistant bridge: {str(e)}")
            raise AssistantBridgeError(f"Initialization failed: {str(e)}")
            
    async def chat(self, message: str) -> str:
        """
        Process a chat message using the assistant.
        
        Args:
            message: The user's message
        
        Returns:
            The assistant's response
        """
        if not self._thread_id:
            await self.initialize()
            
        # Add the message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # If agent service is available, use it
            if AGENT_SERVICES_AVAILABLE and self.agent_service:
                context = {
                    "conversation_history": self.conversation_history,
                    "assistant_id": self.assistant_id
                }
                response = await self.agent_service.run_existing_agent(message, context)
                self.conversation_history.append({"role": "assistant", "content": response})
                return response
            
            # Otherwise fall back to direct API usage
            # Add message to thread
            await self.openai_client.beta.threads.messages.create(
                thread_id=self._thread_id,
                role="user",
                content=message
            )
            
            # Run the assistant
            run = await self.openai_client.beta.threads.runs.create(
                thread_id=self._thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for the run to complete
            while True:
                run_status = await self.openai_client.beta.threads.runs.retrieve(
                    thread_id=self._thread_id,
                    run_id=run.id
                )
                
                if run_status.status == "completed":
                    break
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    raise AssistantBridgeError(f"Run failed with status: {run_status.status}")
                
                await asyncio.sleep(1)
            
            # Get the messages
            messages = await self.openai_client.beta.threads.messages.list(
                thread_id=self._thread_id
            )
            
            # Extract the response text
            response = ""
            for msg in messages.data:
                if msg.role == "assistant":
                    for content_item in msg.content:
                        if content_item.type == "text":
                            response = content_item.text.value
                            break
                    break
            
            # Add to history
            if response:
                self.conversation_history.append({"role": "assistant", "content": response})
                
            return response
        
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise AssistantBridgeError(f"Chat failed: {str(e)}")
    
    async def chat_streaming(self, message: str):
        """Process a chat message with streaming responses."""
        # Add the message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # If agent service is available, use streaming
            if AGENT_SERVICES_AVAILABLE and self.agent_service:
                context = {
                    "conversation_history": self.conversation_history,
                    "assistant_id": self.assistant_id
                }
                
                full_response = ""
                async for event in self.agent_service.run_existing_agent_streaming(message, context):
                    if event.type == "content_chunk":
                        content = event.data.get("content", "")
                        full_response += content
                        yield content, "message"
                    elif event.type == "tool_event":
                        yield event.data.get("message", "Using tool..."), "tool_call"
                
                # Add the response to history
                self.conversation_history.append({"role": "assistant", "content": full_response})
                return
            
            # Otherwise, get the complete response first then simulate streaming
            full_response = await self.chat(message)
            
            # Simulate streaming by breaking the response into chunks
            sentences = full_response.split(". ")
            
            for i, sentence in enumerate(sentences):
                # Add the period back except for the last sentence
                if i < len(sentences) - 1:
                    sentence += "."
                
                # Add a space after the sentence
                sentence += " "
                
                # Yield each sentence
                yield sentence, "message"
                
                # Brief pause to simulate streaming
                await asyncio.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}")
            raise
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history"""
        return self.conversation_history
        
    def clear_history(self) -> None:
        """Clear the conversation history and create a new thread"""
        self.conversation_history = []
        # Create a new thread asynchronously in the background
        if hasattr(self, '_thread_id'):
            asyncio.create_task(self._create_new_thread())
    
    async def _create_new_thread(self):
        """Create a new thread for the conversation."""
        try:
            thread = await self.openai_client.beta.threads.create()
            self._thread_id = thread.id
            logger.info(f"Created new thread: {thread.id}")
        except Exception as e:
            logger.error(f"Failed to create new thread: {str(e)}") 