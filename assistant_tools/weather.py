# import os
# import requests
# from helpers import get_secret_value

# WEATHER_API_KEY = get_secret_value("WEATHER_API_KEY")

# def get_weather_data(location: str) -> dict:
#     """
#     Fetches real-time weather data for a given location.
#     """
#     url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={WEATHER_API_KEY}"
#     headers = {"accept": "application/json"}
#     response = requests.get(url, headers=headers)
#     return response.json()
