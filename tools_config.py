tools_list = [
    {
        "type": "function",
        "function": {

            "name": "get_stock_price",
            "description": "Retrieve the latest closing price of a stock using its ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The ticker symbol of the stock"
                    }
                },
                "required": ["symbol"]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_data",
            "description": "Fetches real-time weather data for a given location using Tomorrow.io's API. The API key is accessed internally within the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location for which to fetch the weather data. Defaults to 'Sydney'."
                    }
                },
                "required": ["location"]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_run_agent_query",
            "description": "Initializes the agent and runs the given query. This function uses an OpenAI model and a Jira API Wrapper to process a Jira query and return the results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "jira_query": {
                        "type": "string",
                        "description": "A string representing the instruction or query to be processed by the agent."
                    }
                },
                "required": ["jira_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_airport_details",
            "description": "Retrieves detailed information about an airport using its ICAO code through the FlightRadar24 API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": "The ICAO airport code for which to retrieve details."
                    }
                },
                "required": ["airport_code"]
            }
        }
    },
]