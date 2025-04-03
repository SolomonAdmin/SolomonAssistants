"""
Runner implementation for executing agents.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RunResult:
    """Result from running an agent."""
    new_items: list = None
    
    def __init__(self):
        self.new_items = []

class Runner:
    """Executes agents and manages their output."""
    
    @staticmethod
    async def run(starting_agent: Any, input: str, context: Optional[Dict[str, Any]] = None) -> RunResult:
        """Run the agent with the given input."""
        result = RunResult()
        response = await starting_agent.run(input, context)
        result.new_items.append(response)
        return result 