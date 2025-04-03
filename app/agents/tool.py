"""
Tool implementations for the agent SDK.
"""
from typing import Dict, Any, Optional, Callable, Union, List

class FunctionTool:
    """Base class for function-based tools."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    async def run(self, *args, **kwargs) -> Any:
        """Execute the tool function."""
        raise NotImplementedError("Subclasses must implement run()")

# Type alias for all possible tool types
Tool = Union[FunctionTool]  # Can add other tool types here if needed 