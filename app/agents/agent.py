"""
Agent implementation for the Solomon Assistants framework.
"""
from typing import List, Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import logging
import json
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
                    schema = tool.to_dict()
                    tool_schemas.append(schema)
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
                            # Parse arguments as JSON, with fallback for non-JSON input
                            try:
                                # Try to parse as JSON first
                                args_str = tool_call.function.arguments.strip()
                                if args_str and args_str.startswith('{') and args_str.endswith('}'):
                                    args = json.loads(args_str)
                                else:
                                    # If not a proper JSON object, extract as query if it's for web_search
                                    if tool.name == "web_search":
                                        args = {"query": args_str if args_str else "IPaaS news"}
                                    else:
                                        args = tool_call.function.arguments
                            except (json.JSONDecodeError, TypeError):
                                logger.warning(f"Invalid JSON arguments for {tool.name}: {tool_call.function.arguments}")
                                # If parsing fails and it's a web search, use a default query
                                if tool.name == "web_search":
                                    query_text = tool_call.function.arguments.strip() if tool_call.function.arguments else "IPaaS news"
                                    args = {"query": query_text}
                                else:
                                    # For other tools, pass the arguments as a string
                                    args = tool_call.function.arguments
                            
                            # Execute tool - log the start of execution
                            logger.info(f"Executing tool {tool.name} with args: {args}")
                            tool_result = await tool.run(args)
                            
                            # Special handling for web search results
                            if tool.name == "web_search":
                                logger.info(f"Web search result received, length: {len(str(tool_result)) if tool_result else 0}")
                                # If the result starts with "Error" or "I tried to search", log it as an error
                                if str(tool_result).startswith(("Error", "I tried to search")):
                                    logger.error(f"Web search error: {str(tool_result)[:100]}...")
                            elif tool.name == "file_search":
                                logger.info(f"File search result received, length: {len(str(tool_result)) if tool_result else 0}")
                                logger.info(f"File search result first 50 chars: {str(tool_result)[:50]}")
                            else:
                                logger.info(f"Tool {tool.name} returned result of length: {len(str(tool_result))}")
                            
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": str(tool_result)
                            })
                        except Exception as e:
                            logger.error(f"Error executing tool {tool.name}: {str(e)}")
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": f"Error executing tool {tool.name}: {str(e)}"
                            })
                    else:
                        logger.warning(f"Tool {tool_call.function.name} not found")
                
                # Add assistant's message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls]
                })
                
                # Add tool outputs
                for output in tool_outputs:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": output["tool_call_id"],
                        "content": output["output"]
                    })
                
                # Get final response
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
        """Run the agent with streaming enabled."""
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
                    schema = tool.to_dict()
                    tool_schemas.append(schema)
                else:
                    logger.warning(f"Tool {tool} does not have to_dict method")
            
            # Create streaming completion using OpenAI client directly
            response = await self.openai_client.chat.completions.create(
                model=self.model.model if hasattr(self.model, 'model') else "gpt-4",
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                tool_choice="auto",
                stream=True,
                temperature=self.model.model_settings.temperature if hasattr(self.model, 'model_settings') else 0.7,
                max_tokens=self.model.model_settings.max_tokens if hasattr(self.model, 'model_settings') else 1000
            )
            
            tool_calls_buffer = []
            current_tool_call = None
            content_buffer = []
            
            async for chunk in response:
                delta = chunk.choices[0].delta
                
                # Handle content chunks
                if hasattr(delta, "content") and delta.content:
                    content_buffer.append(delta.content)
                    yield delta.content
                
                # Handle tool calls
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    tool_call_delta = delta.tool_calls[0]
                    
                    if tool_call_delta.index is not None:  # New tool call
                        if current_tool_call and current_tool_call["function"]["name"]:  # Only add if name is not empty
                            tool_calls_buffer.append(current_tool_call)
                            
                        current_tool_call = {
                            "id": tool_call_delta.id or f"call_{len(tool_calls_buffer)}",
                            "type": "function",
                            "function": {
                                "name": tool_call_delta.function.name or "",
                                "arguments": tool_call_delta.function.arguments or ""
                            }
                        }
                    elif current_tool_call and tool_call_delta.function:
                        if tool_call_delta.function.name:
                            current_tool_call["function"]["name"] += tool_call_delta.function.name
                        if tool_call_delta.function.arguments:
                            current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments
            
            # Add final tool call if any and it has a non-empty name
            if current_tool_call and current_tool_call["function"]["name"]:
                tool_calls_buffer.append(current_tool_call)
            
            # Process tool calls if any were collected
            if tool_calls_buffer:
                tool_outputs = []
                
                for tool_call in tool_calls_buffer:
                    # Skip tool calls with empty names
                    if not tool_call["function"]["name"]:
                        continue
                        
                    # Find matching tool
                    tool_name = tool_call["function"]["name"]
                    tool = next((t for t in self.tools if t.name == tool_name), None)
                    
                    if tool:
                        try:
                            # Parse arguments as JSON, with fallback for non-JSON input
                            try:
                                # Try to parse as JSON first
                                args_str = tool_call["function"]["arguments"].strip()
                                if args_str and args_str.startswith('{') and args_str.endswith('}'):
                                    args = json.loads(args_str)
                                else:
                                    # If not a proper JSON object, extract as query if it's for web_search
                                    if tool_name == "web_search":
                                        args = {"query": args_str if args_str else "IPaaS news"}
                                    else:
                                        args = tool_call["function"]["arguments"]
                            except (json.JSONDecodeError, TypeError):
                                logger.warning(f"Invalid JSON arguments for {tool_name}: {tool_call['function']['arguments']}")
                                # If parsing fails and it's a web search, use a default query
                                if tool_name == "web_search":
                                    query_text = tool_call["function"]["arguments"].strip() if tool_call["function"]["arguments"] else "IPaaS news"
                                    args = {"query": query_text}
                                else:
                                    # For other tools, pass the arguments as a string
                                    args = tool_call["function"]["arguments"]
                            
                            # Execute tool - log the start of execution
                            logger.info(f"Executing tool {tool.name} with args: {args}")
                            tool_result = await tool.run(args)
                            
                            # Special handling for web search results
                            if tool.name == "web_search":
                                logger.info(f"Web search result received, length: {len(str(tool_result)) if tool_result else 0}")
                                # If the result starts with "Error" or "I tried to search", log it as an error
                                if str(tool_result).startswith(("Error", "I tried to search")):
                                    logger.error(f"Web search error: {str(tool_result)[:100]}...")
                            elif tool.name == "file_search":
                                logger.info(f"File search result received, length: {len(str(tool_result)) if tool_result else 0}")
                                logger.info(f"File search result first 50 chars: {str(tool_result)[:50]}")
                            else:
                                logger.info(f"Tool {tool.name} returned result of length: {len(str(tool_result))}")
                            
                            tool_outputs.append({
                                "tool_call_id": tool_call["id"],
                                "output": str(tool_result)
                            })
                        except Exception as e:
                            logger.error(f"Error executing tool {tool.name}: {str(e)}")
                            tool_outputs.append({
                                "tool_call_id": tool_call["id"],
                                "output": f"Error executing tool {tool.name}: {str(e)}"
                            })
                    else:
                        logger.warning(f"Tool {tool_call['function']['name']} not found")
                
                # Only proceed if we have valid tool calls with outputs
                if tool_outputs:
                    # Add assistant's message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_calls_buffer
                    })
                    
                    # Add tool outputs
                    for output in tool_outputs:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": output["tool_call_id"],
                            "content": output["output"]
                        })
                    
                    # Get final response
                    final_response = await self.openai_client.chat.completions.create(
                        model=self.model.model if hasattr(self.model, 'model') else "gpt-4",
                        messages=messages,
                        stream=True,
                        temperature=self.model.model_settings.temperature if hasattr(self.model, 'model_settings') else 0.7,
                        max_tokens=self.model.model_settings.max_tokens if hasattr(self.model, 'model_settings') else 1000
                    )
                    
                    async for chunk in final_response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
            
        except Exception as e:
            logger.error(f"Error in agent stream: {str(e)}")
            raise 