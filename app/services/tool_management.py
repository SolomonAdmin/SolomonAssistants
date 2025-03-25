from typing import List, Dict, Any, Optional, Callable
import logging
import inspect
from agents import Tool, function_tool

logger = logging.getLogger(__name__)

class ToolManagementError(Exception):
    """Base exception for tool management errors."""
    pass

class InvalidToolConfigError(ToolManagementError):
    """Exception raised when the tool configuration is invalid."""
    pass

class ToolNotFoundError(ToolManagementError):
    """Exception raised when a requested tool cannot be found."""
    pass

class ToolManagementService:
    """Service for managing tools that can be used by OpenAI agents."""
    
    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        **kwargs
    ) -> Tool:
        """
        Create a tool from a Python function.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            func: The Python function to use
            **kwargs: Additional arguments for the tool
            
        Returns:
            A Tool instance
            
        Raises:
            InvalidToolConfigError: If the tool configuration is invalid
        """
        if not callable(func):
            raise InvalidToolConfigError("Function must be callable")
            
        try:
            # Create the tool using the function_tool decorator
            tool = function_tool(
                name_override=name,
                description_override=description,
                **kwargs
            )(func)
            
            return tool
            
        except Exception as e:
            logger.error(f"Error creating tool: {str(e)}")
            raise InvalidToolConfigError(f"Error creating tool: {str(e)}")
    
    def create_calculator_tool(self) -> Tool:
        """
        Create a simple calculator tool as an example.
        
        Returns:
            A Tool instance for basic calculations
        """
        def simple_calculator(context: Any, a: float, b: float, operation: str) -> Dict[str, Any]:
            """A simple calculator that can perform basic operations."""
            result = None
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b != 0:
                    result = a / b
                else:
                    raise ValueError("Cannot divide by zero")
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
            return {
                "result": result,
                "operation": operation,
                "a": a,
                "b": b
            }
            
        return self.register_tool(
            name="Calculator",
            description="A simple calculator that can perform basic arithmetic operations (add, subtract, multiply, divide)",
            func=simple_calculator
        ) 