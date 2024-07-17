from typing import Dict, Type
from .base import BaseTool
from .weather.current_temperature import CurrentTemperatureTool
from .workato.workato_tool import WorkatoAssistantFunctionTool

tool_registry: Dict[str, Type[BaseTool]] = {
    "get_current_temperature": CurrentTemperatureTool,
    "send_workato_assistant_request": WorkatoAssistantFunctionTool,
    # Add other tools here
}