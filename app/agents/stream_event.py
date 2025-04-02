"""
Stream event implementation.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StreamEvent:
    """Event for streaming agent output."""
    type: str
    data: Dict[str, Any] 