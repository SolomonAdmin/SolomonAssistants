class BaseTool:
    def __init__(self):
        self.base_url = 'https://55gdlc2st8.execute-api.us-east-1.amazonaws.com'

    def get_headers(self, solomon_consumer_key: str) -> dict:
        return {
            'accept': 'application/json',
            'solomon-consumer-key': solomon_consumer_key,
            'Content-Type': 'application/json'
        }