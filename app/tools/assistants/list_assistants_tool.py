class ListAssistantsTool(BaseTool):
    def execute(self, limit: int = 20, order: str = "desc", solomon_consumer_key: str = None) -> Dict[str, Any]:
        """
        Sends a GET request to list all assistants.

        :param limit: A limit on the number of objects to be returned (between 1 and 100)
        :param order: Sort order by created_at timestamp ('asc' or 'desc')
        :param solomon_consumer_key: User's unique API key for authentication
        :return: The response from the API as a dictionary
        """
        url = f'{self.base_url}/assistant/list_assistants'
        headers = self.get_headers(solomon_consumer_key)
        params = {
            'limit': limit,
            'order': order
        }
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_assistants",
                "description": "Retrieves a list of assistants with pagination support.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "A limit on the number of objects to be returned. Limit can range between 1 and 100.",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "order": {
                            "type": "string",
                            "description": "Sort order by the created_at timestamp of the objects.",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "solomon_consumer_key": {
                            "type": "string",
                            "description": "User's unique API key for authentication."
                        }
                    },
                    "required": ["solomon_consumer_key"]
                }
            }
        }