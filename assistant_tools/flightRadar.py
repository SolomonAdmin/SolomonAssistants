from FlightRadar24 import FlightRadar24API

def get_airport_details(airport_code):
    fr_api = FlightRadar24API()
    airport = fr_api.get_airport(airport_code)
    return airport
