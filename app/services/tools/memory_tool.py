from typing import Dict, Any, Optional, List
from app.agents.tool import FunctionTool
from ..session_memory import SessionMemory

class MemoryTool(FunctionTool):
    """Tool for updating session memory."""
    
    def __init__(self, session_memory: SessionMemory):
        super().__init__(
            name="update_memory_slot",
            description="Update a slot in the session memory with a new value",
            parameters={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The memory slot key to update",
                        "enum": [
                            "user_name",
                            "user_email",
                            "company_name",
                            "departments",
                            "tools_used",
                            "top_pain_points",
                            "current_automation",
                            "automation_goals",
                            "key_metrics",
                            "has_automation_owner",
                            "thread_id"
                        ]
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to store in the memory slot (will be converted to appropriate type)"
                    }
                },
                "required": ["key", "value"]
            }
        )
        self.session_memory = session_memory
    
    async def run(self, key: str, value: Any) -> str:
        """Update the specified memory slot with the given value."""
        self.session_memory.update(key, value)
        return f"Updated memory slot '{key}' with value: {value}"
    
    def add_message_to_history(self, message: Dict[str, Any]) -> None:
        """Add a message to the conversation history."""
        self.session_memory.add_to_history(message)
    
    def get_conversation_context(self, n_messages: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self.session_memory.get_recent_context(n_messages)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary format for OpenAI API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        } 