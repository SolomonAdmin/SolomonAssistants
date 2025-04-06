from typing import Optional, Dict, Any, AsyncGenerator, List
from datetime import datetime
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
from app.agents.tools import WebSearchTool, FileSearchToolWrapper
from agents import FileSearchTool  # Import FileSearchTool from external package

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
            
            # Add web search tool with the API key
            web_search_tool = WebSearchTool()
            # Set the client directly to ensure it has access to the API key
            web_search_tool.client = self.openai_client
            tools.append(web_search_tool)
            logger.info("Added WebSearchTool to agent tools")
            
            # Add other tools...
            if vector_store_ids:
                logger.info(f"Attempting to add FileSearchTool with vector_store_ids: {vector_store_ids}")
                # Check FileSearchTool parameters
                import inspect
                try:
                    sig = inspect.signature(FileSearchTool.__init__)
                    logger.info(f"FileSearchTool parameters: {list(sig.parameters.keys())}")
                except Exception as e:
                    logger.error(f"Error inspecting FileSearchTool: {str(e)}")
                
                for vs_id in vector_store_ids:
                    try:
                        logger.info(f"Creating FileSearchTool with vector_store_id: {vs_id}")
                        # Try both parameter names
                        try:
                            # Try singular version first (most common)
                            original_tool = FileSearchTool(vector_store_id=vs_id)
                            logger.info("Created original FileSearchTool with singular parameter 'vector_store_id'")
                        except TypeError:
                            try:
                                # If that fails, try plural version
                                original_tool = FileSearchTool(vector_store_ids=[vs_id])
                                logger.info("Created original FileSearchTool with plural parameter 'vector_store_ids'")
                            except Exception as e:
                                logger.error(f"Could not create FileSearchTool with either parameter name: {str(e)}")
                                continue
                        
                        # Wrap the original tool with our wrapper
                        file_search = FileSearchToolWrapper(original_tool, vs_id)
                        
                        # Ensure it has access to the OpenAI client if needed
                        file_search.client = self.openai_client
                        logger.info("Set OpenAI client for FileSearchToolWrapper")
                        
                        tools.append(file_search)
                        logger.info(f"Successfully added FileSearchToolWrapper with vector_store_id: {vs_id}")
                    except Exception as e:
                        logger.error(f"Error creating FileSearchTool with vector_store_id {vs_id}: {str(e)}")
            else:
                logger.info("No vector_store_ids provided, skipping FileSearchTool")
            
            if workato_integration:
                workato_tools = workato_integration.get_tools()
                tools.extend(workato_tools)
            
            # Create the model
            model = OpenAIResponsesModel(
                openai_client=self.openai_client,
                model=assistant.model
            )
            model.model_settings = ModelSettings(temperature=0.7, max_tokens=1000)
            
            # Create the agent
            instructions = assistant.instructions + "\nYou have access to a web_search tool to find current information. When users ask about news (e.g., 'search for IPaaS news'), use the web_search tool with query parameter containing the search terms. Always include the query parameter in proper JSON format like this: {\"query\": \"IPaaS news\"}. After receiving the search results, share them with the user immediately and completely."
            
            # Add file search instructions if available
            if vector_store_ids:
                instructions += "\n\nYou also have access to a file_search tool to search documents in the vector database. ALWAYS use this tool when users ask about documents, files, or what data you have access to. When you see the file_search results, quote them directly to the user - they contain important information about available documents. Examples of when to use file_search:\n- 'What documents do you have?'\n- 'Can you give me an overview of your files?'\n- 'Search for X in your documents'\n\nTo use the file_search tool, pass a query parameter in proper JSON format like this: {\"query\": \"document overview\"}. NEVER respond that you don't have access to documents - ALWAYS use the file_search tool and share its full response with the user."
            
            self.agent = Agent(
                name=assistant.name or "Assistant",
                instructions=instructions,
                tools=tools,
                model=model
            )
            
            self.initialized = True
            logger.info(f"Agent initialized from assistant {assistant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise
    
    def _prepare_context_with_history(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare context with conversation history and memory."""
        context = context or {}
        
        # Get recent conversation history
        recent_history = self.session_memory.get_recent_context(n_messages=5)
        
        # Get all persistent memory slots
        memory_data = self.session_memory.get_all()
        
        # Prepare context with both conversation history and memory slots
        context.update({
            "conversation_history": recent_history,
            "session_memory": {k: v for k, v in memory_data.items() if v is not None and k != "conversation_history"},
            "current_input": user_input
        })
        
        return context
    
    def _save_interaction(self, user_input: str, assistant_response: str) -> None:
        """Save the interaction to conversation history."""
        # Save user message
        self.session_memory.add_to_history({
            "role": "user",
            "content": user_input
        })
        
        # Save assistant response
        self.session_memory.add_to_history({
            "role": "assistant",
            "content": assistant_response
        })
    
    async def run_existing_agent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Run the agent with the given input text and context."""
        if not self.agent or not self.initialized:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # Prepare context with history
            enriched_context = self._prepare_context_with_history(input_text, context)
            
            # Run the agent
            result = await Runner.run(
                starting_agent=self.agent,
                input=input_text,
                context=enriched_context
            )
            
            # Extract the output from the result
            output = ""
            if result.new_items:
                for item in reversed(result.new_items):
                    if isinstance(item, MessageOutputItem):
                        if hasattr(item, 'message') and hasattr(item.message, 'content'):
                            output = item.message.content
                            break
                        elif hasattr(item, 'raw_item'):
                            if hasattr(item.raw_item, 'content') and isinstance(item.raw_item.content, list):
                                content_texts = []
                                for content_item in item.raw_item.content:
                                    if hasattr(content_item, 'text'):
                                        content_texts.append(content_item.text)
                                
                                if content_texts:
                                    output = "\n".join(content_texts)
                                    break
            
            # Save the interaction to history
            if output:
                self._save_interaction(input_text, output)
            
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
            # Prepare context with history
            enriched_context = self._prepare_context_with_history(input_text, context)
            
            # First yield a starting event
            yield StreamEvent(type="system", data={"message": "Starting agent processing"})
            
            # Collect the full response for history
            full_response = []
            
            # Get the agent's response using streaming
            async for content in self.agent.run_stream(input_text, enriched_context):
                full_response.append(content)
                yield StreamEvent(type="content_chunk", data={"content": content})
            
            # Save the complete interaction to history
            if full_response:
                self._save_interaction(input_text, "".join(full_response))
            
            # Final completion event
            yield StreamEvent(type="completion", data={"message": "Processing completed"})
            
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            raise 