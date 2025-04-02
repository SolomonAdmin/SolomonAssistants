"""
Message output item implementation.
"""
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class MessageOutputItem:
    """Represents a message output from an agent."""
    message: Any
    raw_item: Optional[Any] = None
    tool_calls: Optional[list] = None 