from typing import Optional, Dict, Any, AsyncGenerator, List
import asyncio
import logging
from dataclasses import dataclass
from openai import AsyncOpenAI

# Import from agents SDK 
from app.agents.agent import Agent, ModelSettings
from app.agents.runner import Runner
from app.agents.openai_responses_model import OpenAIResponsesModel
from app.agents.message_output_item import MessageOutputItem
from app.agents.stream_event import StreamEvent

# Import local services
from .model_management import ModelManagementService
from .tool_management import ToolManagementService
from .workato_integration import WorkatoIntegration
from .tools.memory_tool import MemoryTool
from .session_memory import SessionMemory

logger = logging.getLogger(__name__)

@dataclass
class StreamEvent:
    """Custom event class for streaming events."""
    type: str
    data: Dict[str, Any]

AGENTS_SDK_AVAILABLE = True

class AgentService:
    """Service for managing and running Agents."""
    
    def __init__(self, api_key: str):
        """Initialize with an API key."""
        self.api_key = api_key
        self.agent = None
        self.openai_client = AsyncOpenAI(api_key=api_key)
        self.session_memory = SessionMemory()
        self.initialized = False
    
    async def initialize(self, 
                        assistant_id: str, 
                        vector_store_ids: Optional[List[str]] = None,
                        workato_integration: Optional[Any] = None) -> bool:
        """Initialize the agent service with optional integrations."""
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("Agents SDK not available")
            return False
            
        try:
            # Get assistant details
            assistant = await self.openai_client.beta.assistants.retrieve(assistant_id)
            
            # Configure tools
            tools = []
            
            # Add memory tool
            memory_tool = MemoryTool(self.session_memory)
            tools.append(memory_tool)
            
            # Add other tools...
            if vector_store_ids:
                for vs_id in vector_store_ids:
                    file_search = FileSearchTool(vector_store_id=vs_id)
                    tools.append(file_search)
            
            if workato_integration:
                workato_tools = workato_integration.get_tools()
                tools.extend(workato_tools)
            
            # Create the model
            model = OpenAIResponsesModel(
                openai_client=self.openai_client,
                model=assistant.model
            )
            
            # Create the agent
            self.agent = Agent(
                name=assistant.name or "Assistant",
                instructions=assistant.instructions,
                tools=tools,
                model=model
            )
            
            self.initialized = True
            logger.info(f"Agent initialized from assistant {assistant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise
    
    async def run_existing_agent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Run the agent with the given input text and context."""
        if not self.agent or not self.initialized:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # Add session memory to context
            context = context or {}
            context["session_memory"] = self.session_memory.get_all()
            
            # Run the agent
            result = await Runner.run(
                starting_agent=self.agent,
                input=input_text,
                context=context
            )
            
            # Extract the output from the result
            output = ""
            if result.new_items:
                for item in reversed(result.new_items):
                    # Find a MessageOutputItem to get the final response
                    if isinstance(item, MessageOutputItem):
                        if hasattr(item, 'message') and hasattr(item.message, 'content'):
                            output = item.message.content
                            break
                        # Fallback to raw_item if available
                        elif hasattr(item, 'raw_item'):
                            if hasattr(item.raw_item, 'content') and isinstance(item.raw_item.content, list):
                                # Combine all text from content items
                                content_texts = []
                                for content_item in item.raw_item.content:
                                    if hasattr(content_item, 'text'):
                                        content_texts.append(content_item.text)
                                
                                if content_texts:
                                    output = "\n".join(content_texts)
                                    break
            
            return output
            
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            raise
    
    async def run_existing_agent_streaming(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Run the agent with streaming enabled."""
        if not self.agent or not self.initialized:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # Add session memory to context
            context = context or {}
            context["session_memory"] = self.session_memory.get_all()
            
            # First yield a starting event
            yield StreamEvent(type="system", data={"message": "Starting agent processing"})
            
            # Get the agent's response using streaming
            async for content in self.agent.run_stream(input_text, context):
                yield StreamEvent(type="content_chunk", data={"content": content})
            
            # Final completion event
            yield StreamEvent(type="completion", data={"message": "Processing completed"})
            
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            raise 