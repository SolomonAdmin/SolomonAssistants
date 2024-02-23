from FlightRadar24 import FlightRadar24API
class FlightRadarTool:
    def __init__(self):
        self.fr_api = FlightRadar24API()

    def get_airport_details(self, airport_code):
        airport = self.fr_api.get_airport(airport_code)
        return str(airport)
