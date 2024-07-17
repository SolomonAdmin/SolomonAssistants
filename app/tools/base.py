from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        pass