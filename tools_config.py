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
]