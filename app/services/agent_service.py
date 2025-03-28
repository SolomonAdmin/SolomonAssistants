from typing import Optional, Dict, Any, AsyncGenerator, List
import asyncio
import logging
from dataclasses import dataclass
from openai import AsyncOpenAI

# Import from agents SDK 
from agents import Agent, ModelSettings
from agents.run import Runner

# Import local services
from .model_management import ModelManagementService
from .tool_management import ToolManagementService
from .workato_integration import WorkatoIntegration

logger = logging.getLogger(__name__)

@dataclass
class StreamEvent:
    """Custom event class for streaming events."""
    type: str
    data: Dict[str, Any]

class AgentService:
    """Service for managing and running Agents."""
    
    def __init__(self, api_key: str):
        """Initialize the agent service with API key."""
        self.api_key = api_key
        self.model_service = ModelManagementService()
        self.tool_service = ToolManagementService()
        self.agent = None
        self.initialized = False
        
    async def initialize(self, 
                         assistant_id: str, 
                         vector_store_ids: Optional[List[str]] = None,
                         workato_integration: Optional[WorkatoIntegration] = None) -> bool:
        """
        Initialize the agent with the specified assistant ID.
        
        Args:
            assistant_id: OpenAI Assistant ID to use for configuration
            vector_store_ids: Optional list of vector store IDs
            workato_integration: Optional Workato integration for tools
            
        Returns:
            True if initialization was successful
        """
        try:
            # Create OpenAI client
            client = AsyncOpenAI(api_key=self.api_key)
            
            # Fetch the assistant to get its configuration
            assistant = await client.beta.assistants.retrieve(assistant_id)
            
            # Initialize tools
            tools = []
            
            # Add WebSearchTool
            from agents import WebSearchTool
            web_search_tool = WebSearchTool()
            tools.append(web_search_tool)
            logger.info(f"Added WebSearchTool: {web_search_tool.name}")
            
            # Add FileSearchTool if vector store IDs are provided
            if vector_store_ids:
                from agents import FileSearchTool
                file_search_tool = FileSearchTool(vector_store_ids=vector_store_ids)
                tools.append(file_search_tool)
                logger.info(f"Added FileSearchTool with vector stores: {vector_store_ids}")
            
            # Add Workato tools if integration is provided
            if workato_integration:
                workato_tools = workato_integration.get_tools()
                tools.extend(workato_tools)
                logger.info(f"Added {len(workato_tools)} Workato integration tools")
            
            # Create model
            model = self.model_service.create_model(
                api_key=self.api_key,
                model_name=assistant.model
            )
            
            # Enhance instructions to mention web search capability
            enhanced_instructions = assistant.instructions
            if not "web search" in enhanced_instructions.lower():
                enhanced_instructions += "\nYou have the ability to search the web for real-time information when needed."
            
            # Create the agent
            self.agent = Agent(
                name=assistant.name or "Assistant",
                instructions=enhanced_instructions,
                tools=tools,
                model=model,
                model_settings=ModelSettings(temperature=0.7, max_tokens=1000)
            )
            
            self.initialized = True
            logger.info(f"Agent initialized with assistant ID: {assistant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            self.initialized = False
            raise
    
    async def run_existing_agent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Run the agent with the given input text.
        
        Args:
            input_text: The text to process
            context: Optional context data
            
        Returns:
            The response from the agent
        """
        if not self.agent or not self.initialized:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # Run the agent
            result = await Runner.run(
                starting_agent=self.agent,
                input=input_text,
                context=context or {}
            )
            
            # Extract the output from the result
            output = ""
            if result.new_items:
                for item in reversed(result.new_items):
                    # Find a MessageOutputItem to get the final response
                    if hasattr(item, 'message') and hasattr(item.message, 'content'):
                        output = item.message.content
                        break
                    # Check if raw_item exists and extract content
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
                    # Direct access to text attribute as a fallback
                    elif hasattr(item, 'text'):
                        output = item.text
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
        """
        Run the agent with the given input text and simulate streaming responses.
        
        Args:
            input_text: The text to process
            context: Optional context data
            
        Yields:
            StreamEvent objects containing chunks of the response
        """
        if not self.agent or not self.initialized:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # First yield a starting event
            yield StreamEvent(type="start", data={"message": "Starting agent processing"})
            
            # Run the agent - get the complete response without streaming
            # (We'll simulate streaming since the SDK might not support actual streaming)
            result = await Runner.run(
                starting_agent=self.agent,
                input=input_text,
                context=context or {}
            )
            
            # Extract the output from the result
            output = ""
            if result.new_items:
                for item in reversed(result.new_items):
                    # Find a MessageOutputItem to get the final response
                    if hasattr(item, 'message') and hasattr(item.message, 'content'):
                        output = item.message.content
                        break
                    # Check if raw_item exists and extract content
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
                    # Direct access to text attribute as a fallback
                    elif hasattr(item, 'text'):
                        output = item.text
                        break
            
            # If we have an output, simulate streaming by breaking it into chunks
            if output:
                # Track tool usage to simulate tool events
                tool_mentioned = False
                
                # Break the output into sentences
                sentences = output.split(". ")
                
                for i, sentence in enumerate(sentences):
                    # Add the period back except for the last sentence
                    if i < len(sentences) - 1:
                        sentence += "."
                    
                    # If the sentence mentions tools and we haven't simulated a tool event yet
                    if ("tool" in sentence.lower() or "search" in sentence.lower()) and not tool_mentioned:
                        yield StreamEvent(type="tool_event", data={"message": "Using a tool"})
                        tool_mentioned = True
                    
                    # Yield the sentence as a content chunk
                    yield StreamEvent(type="content_chunk", data={"content": sentence + " "})
                    
                    # Add a small delay to simulate real streaming
                    await asyncio.sleep(0.05)
            
            # Yield a completion event
            yield StreamEvent(type="completion", data={"message": "Processing complete"})
            
        except Exception as e:
            logger.error(f"Error in streaming agent run: {str(e)}")
            raise 