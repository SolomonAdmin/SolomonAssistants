from typing import Dict, List, Any, Optional, Callable
import logging
import json
import aiohttp
from dataclasses import dataclass

try:
    from agents import Tool, function_tool
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False
    # Create dummy classes/functions for typing
    class Tool: pass
    def function_tool(*args, **kwargs): return lambda x: x

logger = logging.getLogger(__name__)

@dataclass
class WorkatoConfig:
    """Configuration for Workato API."""
    api_token: str
    endpoint_url: str

class WorkatoIntegration:
    """Integration with Workato for system actions and tools."""
    
    def __init__(self, config: WorkatoConfig):
        """Initialize the Workato integration."""
        self.config = config
    
    def get_tools(self) -> List[Tool]:
        """Get the list of Workato tools."""
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("Agents SDK not available, returning empty tools list")
            return []
            
        tools = []
        
        @function_tool(
            name_override="execute_workato_action",
            description_override="""Execute any action through Workato. Available actions include searching or creating contacts in Salesforce.
            The action_type specifies what operation to perform (e.g., 'search_contact', 'create_contact').
            The system parameter indicates which system to interact with (e.g., 'salesforce', 'hubspot').
            The payload_json should be a JSON string containing the data for the action."""
        )
        async def execute_workato_action(action_type: str, system: str, payload_json: str) -> Dict[str, Any]:
            """Execute an action via Workato.
            
            Args:
                action_type: The type of action to execute (e.g., 'search_contact', 'create_contact')
                system: The system to interact with (e.g., 'salesforce', 'hubspot')
                payload_json: JSON string containing the data payload for the action
            
            Returns:
                Dict containing success status, data/error message, and optional result data
            """
            try:
                # For search_contact actions, ensure we use contact_name
                if action_type == "search_contact":
                    try:
                        # Parse existing payload
                        payload_dict = json.loads(payload_json)
                        # If name is provided, convert it to contact_name
                        if "name" in payload_dict:
                            payload_dict["contact_name"] = payload_dict.pop("name")
                        # If neither exists, create contact_name
                        if "contact_name" not in payload_dict:
                            return {
                                "success": False,
                                "error": "Missing contact_name in payload"
                            }
                        # Convert back to JSON string
                        payload_json = json.dumps(payload_dict)
                    except json.JSONDecodeError as e:
                        return {
                            "success": False,
                            "error": f"Invalid payload JSON: {str(e)}"
                        }

                async with aiohttp.ClientSession() as session:
                    headers = {
                        "API-TOKEN": self.config.api_token,
                        "Content-Type": "application/json"
                    }
                    
                    # Format the payload according to Workato's expected structure
                    request_payload = {
                        "action_type": action_type,
                        "system": system,
                        "payload": payload_json,  # JSON string with correct field names
                        "schema": "{}"  # Empty schema as a JSON string
                    }
                    
                    # Log the complete request details
                    logger.info("=== Workato API Request Details ===")
                    logger.info(f"Endpoint URL: {self.config.endpoint_url}")
                    logger.info(f"Headers: {json.dumps(headers, indent=2)}")
                    logger.info(f"Request Payload: {json.dumps(request_payload, indent=2)}")
                    logger.info("================================")
                    
                    async with session.post(
                        self.config.endpoint_url,
                        headers=headers,
                        json=request_payload
                    ) as response:
                        response_text = await response.text()
                        logger.info("=== Workato API Response ===")
                        logger.info(f"Status Code: {response.status}")
                        logger.info(f"Response Body: {response_text}")
                        logger.info("===========================")
                        
                        if response.status == 200:
                            result = json.loads(response_text)
                            return {
                                "success": True,
                                "data": result,
                                "message": f"Action '{action_type}' on system '{system}' completed successfully"
                            }
                        else:
                            logger.error(f"Error executing action: {response_text}")
                            return {
                                "success": False,
                                "error": f"Failed to execute action: {response_text}"
                            }
                            
            except Exception as e:
                logger.error(f"Error in execute_workato_action: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error executing action: {str(e)}"
                }
        
        tools.append(execute_workato_action)
        return tools 