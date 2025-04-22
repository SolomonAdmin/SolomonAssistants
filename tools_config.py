tools_list = [
    {
        "type": "function",
        "function": {
            "name": "send_post_request",
            "description": "Sends a POST request to the Workato assistant function endpoint with specified data. It is used to notify about events or actions, characterized by the 'type' parameter in the request body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "description": "The value to be sent in the request body under the key 'type'. This parameter dictates the nature of the request being sent, for example, 'failed' to indicate a failure event."
                    }
                },
                "required": ["data_type"]
            }
        }
    },
]