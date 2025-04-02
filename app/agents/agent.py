"""
Agent implementation for the Solomon Assistants framework.
"""
from typing import List, Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

@dataclass
class ModelSettings:
    """Settings for the model."""
    temperature: float = 0.7
    max_tokens: int = 1000

@dataclass
class MessageOutputItem:
    """Represents a message output from the agent."""
    message: Any
    raw_item: Any = None

class Agent:
    """Base agent class."""
    
    def __init__(self, name: str, instructions: str, tools: List[Any] = None, model: Any = None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
        self.handoff_description = ""  # For compatibility with OpenAI Assistants
        # Extract OpenAI client from model if available
        self.openai_client = getattr(model, 'client', None) if model else None

    async def run(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> MessageOutputItem:
        """Run the agent with the given input.
        
        Args:
            input_text: The user's input text
            context: Optional context dictionary containing session memory or other data
            
        Returns:
            MessageOutputItem containing the agent's response
        """
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not available. Make sure model was initialized with a client.")

            # Create messages array with system instructions and user input
            messages = [
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": input_text}
            ]
            
            # Add context to system message if provided
            if context:
                context_str = "\nContext:\n" + "\n".join(f"{k}: {v}" for k, v in context.items())
                messages[0]["content"] += context_str
            
            # Get available tool schemas
            tool_schemas = []
            for tool in self.tools:
                if hasattr(tool, "to_dict"):
                    tool_schemas.append(tool.to_dict())
                else:
                    logger.warning(f"Tool {tool} does not have to_dict method")
            
            # Create completion with tools using OpenAI client directly
            response = await self.openai_client.chat.completions.create(
                model=self.model.model if hasattr(self.model, 'model') else "gpt-4",
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                tool_choice="auto",
                temperature=self.model.model_settings.temperature if hasattr(self.model, 'model_settings') else 0.7,
                max_tokens=self.model.model_settings.max_tokens if hasattr(self.model, 'model_settings') else 1000
            )
            
            # Process the response
            if not response.choices:
                raise ValueError("No response choices available")
                
            message = response.choices[0].message
            
            # Handle tool calls if present
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_outputs = []
                
                for tool_call in message.tool_calls:
                    # Find matching tool
                    tool = next((t for t in self.tools if t.name == tool_call.function.name), None)
                    
                    if tool:
                        try:
                            # Execute tool
                            tool_result = await tool.run(tool_call.function.arguments)
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": str(tool_result)
                            })
                        except Exception as e:
                            logger.error(f"Error executing tool {tool.name}: {str(e)}")
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": f"Error: {str(e)}"
                            })
                    else:
                        logger.warning(f"Tool {tool_call.function.name} not found")
                
                # Add tool outputs to messages and get final response
                messages.append(message)
                for output in tool_outputs:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": output["tool_call_id"],
                        "content": output["output"]
                    })
                
                final_response = await self.openai_client.chat.completions.create(
                    model=self.model.model if hasattr(self.model, 'model') else "gpt-4",
                    messages=messages,
                    temperature=self.model.model_settings.temperature if hasattr(self.model, 'model_settings') else 0.7,
                    max_tokens=self.model.model_settings.max_tokens if hasattr(self.model, 'model_settings') else 1000
                )
                
                if not final_response.choices:
                    raise ValueError("No final response choices available")
                    
                message = final_response.choices[0].message
            
            return MessageOutputItem(message=message, raw_item=response)
            
        except Exception as e:
            logger.error(f"Error in agent run: {str(e)}")
            raise
            
    async def run_stream(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """Run the agent with streaming enabled.
        
        Args:
            input_text: The user's input text
            context: Optional context dictionary containing session memory or other data
            
        Yields:
            Chunks of the agent's response as they are generated
        """
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not available. Make sure model was initialized with a client.")

            # Create messages array with system instructions and user input
            messages = [
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": input_text}
            ]
            
            # Add context to system message if provided
            if context:
                context_str = "\nContext:\n" + "\n".join(f"{k}: {v}" for k, v in context.items())
                messages[0]["content"] += context_str
            
            # Create streaming completion using OpenAI client directly
            response = await self.openai_client.chat.completions.create(
                model=self.model.model if hasattr(self.model, 'model') else "gpt-4",
                messages=messages,
                stream=True,
                temperature=self.model.model_settings.temperature if hasattr(self.model, 'model_settings') else 0.7,
                max_tokens=self.model.model_settings.max_tokens if hasattr(self.model, 'model_settings') else 1000
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in agent stream: {str(e)}")
            raise 