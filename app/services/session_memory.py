from typing import Dict, Any, List, Optional
from datetime import datetime

class SessionMemory:
    """Manages session-based memory for agent conversations."""
    
    def __init__(self):
        self.memory = {
            "user_name": None,
            "user_email": None,
            "company_name": None,
            "departments": [],
            "tools_used": [],
            "top_pain_points": None,
            "current_automation": None,
            "automation_goals": None,
            "key_metrics": None,
            "has_automation_owner": None,
            "conversation_history": [],
            "last_context": None,
            "thread_id": None
        }
        self.max_history_length = 50  # Maximum number of messages to keep in history
    
    def update(self, key: str, value: Any) -> None:
        """Update a memory slot with a new value."""
        if key in self.memory:
            self.memory[key] = value
    
    def get(self, key: str) -> Any:
        """Get the value of a memory slot."""
        return self.memory.get(key)
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire memory dictionary."""
        return self.memory.copy()
    
    def clear(self) -> None:
        """Clear all memory slots."""
        for key in self.memory:
            if isinstance(self.memory[key], list):
                self.memory[key] = []
            else:
                self.memory[key] = None
    
    def add_to_history(self, message: Dict[str, Any]) -> None:
        """Add a message to the conversation history with timestamp."""
        history_entry = {
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["conversation_history"].append(history_entry)
        
        # Keep history within size limit by removing oldest messages if needed
        if len(self.memory["conversation_history"]) > self.max_history_length:
            self.memory["conversation_history"] = self.memory["conversation_history"][-self.max_history_length:]
    
    def get_recent_context(self, n_messages: int = 5) -> List[Dict[str, Any]]:
        """Get the n most recent messages from conversation history."""
        history = self.memory["conversation_history"]
        return history[-n_messages:] if history else []
    
    def set_thread_id(self, thread_id: str) -> None:
        """Set the thread ID for the current conversation."""
        self.memory["thread_id"] = thread_id
    
    def get_thread_id(self) -> Optional[str]:
        """Get the current thread ID."""
        return self.memory["thread_id"] 