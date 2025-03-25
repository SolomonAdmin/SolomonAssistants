"""
Stub module for agents when the real agents package isn't available.
This allows imports to work without errors.
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Generic, TypeVar, List, Dict, Optional

# Define a type variable for the context
TContext = TypeVar("TContext")

@dataclass
class ModelSettings:
    """Model settings for agents."""
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: Optional[int] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop: Optional[List[str]] = None

class Tool:
    """Stub for a Tool class"""
    pass

def function_tool(*args, **kwargs):
    """Stub for function_tool decorator"""
    def decorator(func):
        return func
    return decorator

@dataclass
class Agent:
    """Stub for Agent class"""
    name: str
    instructions: str = None
    model: Any = None
    tools: List[Tool] = field(default_factory=list)

class OpenAIChatCompletionsModel:
    """Stub for OpenAI Chat Completions Model"""
    def __init__(self, model: str, openai_client: Any = None):
        self.model = model
        self.openai_client = openai_client
        self.model_settings = ModelSettings()

class OpenAIResponsesModel:
    """Stub for OpenAI Responses Model"""
    def __init__(self, model: str, openai_client: Any = None):
        self.model = model
        self.openai_client = openai_client
        self.model_settings = ModelSettings()

class Runner:
    """Stub for Runner class"""
    @staticmethod
    async def run(starting_agent: Agent, input: str, context: Dict[str, Any] = None):
        """Stub implementation"""
        class RunResult:
            def __init__(self):
                class Item:
                    def __init__(self, text="Response from agent"):
                        self.text = text
                self.new_items = [Item()]
        return RunResult() 