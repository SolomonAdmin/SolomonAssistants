from typing import Dict, Type
from .base import BaseTool
# from .weather.current_temperature import CurrentTemperatureTool
from .workato.workato_tool import WorkatoAssistantFunctionTool
from .assistants.create_assistant_tool import CreateAssistantTool
from .assistants.list_assistants_tool import ListAssistantsTool
from .assistants.modify_assistant_tool import ModifyAssistantTool
from .assistants.delete_assistant_tool import DeleteAssistantTool
from .assistants.call_agent_tool import CallAgentTool
from .workato_action_tool.workato_action_tool import WorkatoActionTool

tool_registry: Dict[str, Type[BaseTool]] = {
    # "get_current_temperature": CurrentTemperatureTool,
    "send_workato_assistant_request": WorkatoAssistantFunctionTool,
    "create_assistant": CreateAssistantTool,
    "list_assistants": ListAssistantsTool,
    "modify_assistant": ModifyAssistantTool,
    "delete_assistant": DeleteAssistantTool,
    "call_agent": CallAgentTool,
    "execute_workato_action": WorkatoActionTool,
}