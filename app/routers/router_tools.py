from fastapi import APIRouter
from tools import tool_registry

tool_available_router = APIRouter(tags=["Tools Available - function calls"])

@tool_available_router.get("/tools", response_model=dict)
async def get_available_tools():
    tools = {}
    for tool_name, tool_class in tool_registry.items():
        tool_instance = tool_class()
        tools[tool_name] = tool_instance.get_definition()["function"]
    return tools
