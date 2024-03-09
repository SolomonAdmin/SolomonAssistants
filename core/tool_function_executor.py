# core/tool_function_executor.py

import asyncio
import json

class ToolFunctionExecutor:
    def __init__(self, tool_functions: dict):
        """
        Initializes the ToolFunctionExecutor with a mapping of tool function names to their implementations.

        Args:
            tool_functions (dict): A dictionary mapping tool function names to callable implementations.
        """
        self.tool_functions = tool_functions

    async def execute_tool_functions(self, required_actions: dict) -> list:
        """
        Executes the required tool functions based on the assistant's requirements and returns their outputs.

        Args:
            required_actions (dict): A dictionary detailing the required actions and their arguments.

        Returns:
            list: A list of results from the executed tool functions.
        """
        tool_outputs = []
        for action in required_actions.get("tool_calls", []):
            func_name = action.get('function', {}).get('name')
            if func_name in self.tool_functions:
                arguments = json.loads(action.get('function', {}).get('arguments', '{}'))
                output = await asyncio.to_thread(self.tool_functions[func_name], **arguments)
                tool_outputs.append({
                    "tool_call_id": action.get('id'),
                    "output": output
                })
            else:
                raise ValueError(f"Unknown tool function: {func_name}")
        return tool_outputs
