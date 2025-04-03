from typing import Optional, Dict, Any
import asyncio
from log import logger
from agents.runner import Runner
from agents.message_output_item import MessageOutputItem
from agents.stream_event import StreamEvent

class AgentManagement:
    def __init__(self, agent):
        self.agent = agent

    async def run_existing_agent_streaming(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Run the agent with streaming enabled - simulating streaming since Runner.stream doesn't exist."""
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # First yield a starting event
            yield StreamEvent(type="start", data={"message": "Starting agent processing"})
            
            # Run the agent - get the complete response without streaming
            result = await Runner.run(
                starting_agent=self.agent,
                input=input_text,
                context=context or {}
            )
            
            # Extract the output from the result
            output = ""
            if result.new_items:
                for item in result.new_items:
                    # Look for MessageOutputItem to get the response text
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