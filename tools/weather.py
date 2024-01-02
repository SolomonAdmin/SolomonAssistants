import os
import requests
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather_data(location: str) -> dict:
    """
    Fetches real-time weather data for a given location.
    """
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={WEATHER_API_KEY}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()
