from typing import Dict, Any, List, Optional

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
            "has_automation_owner": None
        }
    
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