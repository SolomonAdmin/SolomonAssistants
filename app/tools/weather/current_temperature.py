# from typing import Dict, Any
# from .open_meteo_api import get_weather_data

# class CurrentTemperatureTool:  # Remove the inheritance from BaseTool for now
#     def execute(self, latitude: str, longitude: str, unit: str) -> float:
#         params = {
#             "latitude": float(latitude),
#             "longitude": float(longitude),
#             "current": "temperature_2m"
#         }
#         temperature = get_weather_data(params)
        
#         # The API returns temperature in Celsius by default
#         if unit.lower() == "fahrenheit":
#             temperature = (temperature * 9/5) + 32
        
#         return round(temperature, 2)

#     def get_definition(self) -> Dict[str, Any]:
#         return {
#             "type": "function",
#             "function": {
#                 "name": "get_current_temperature",
#                 "description": "Get the current temperature for a specific location",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "latitude": {
#                             "type": "string",
#                             "description": "The latitude of the location."
#                         },
#                         "longitude": {
#                             "type": "string",
#                             "description": "The longitude of the location."
#                         },
#                         "unit": {
#                             "type": "string",
#                             "enum": ["Celsius", "Fahrenheit"],
#                             "description": "The temperature unit to use."
#                         }
#                     },
#                     "required": ["latitude", "longitude", "unit"]
#                 }
#             }
#         }

# # # Add this at the end of the file for testing
# # if __name__ == "__main__":
# #     tool = CurrentTemperatureTool()
    
# #     # Test for New York City
# #     latitude = "40.7128"
# #     longitude = "-74.0060"
    
# #     # Test in Celsius
# #     result_celsius = tool.execute(latitude, longitude, "Celsius")
# #     print(f"Current temperature in New York City (Celsius): {result_celsius}°C")
    
# #     # Test in Fahrenheit
# #     result_fahrenheit = tool.execute(latitude, longitude, "Fahrenheit")
# #     print(f"Current temperature in New York City (Fahrenheit): {result_fahrenheit}°F")