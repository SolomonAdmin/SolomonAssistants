from typing import List, Dict, Any
from models.models_threads import Thread
from rds_db_connection import DatabaseConnector
import requests
from utils import get_headers

class ThreadService:
    def __init__(self):
        self.db = DatabaseConnector()

    def get_threads(self, solomon_consumer_key: str) -> List[Thread]:
        threads = self.db.get_threads(solomon_consumer_key)
        return [Thread(**thread) for thread in threads]

    def create_thread_service(self, thread_data: Dict[str, Any], openai_api_key: str) -> dict:
        """
        Create a new thread using the OpenAI API.
        
        Args:
            thread_data (Dict[str, Any]): Optional thread data including messages, tool_resources, and metadata
            openai_api_key (str): OpenAI API key for authentication
            
        Returns:
            dict: The created thread object from OpenAI's response
        """
        url = "https://api.openai.com/v1/threads"
        headers = {
            **get_headers(openai_api_key),
            'OpenAI-Beta': 'assistants=v2'
        }
        
        try:
            response = requests.post(url, headers=headers, json=thread_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error creating thread: {e}")
            if hasattr(e, 'response') and e.response is not None:
                error_detail = e.response.json().get('error', {}).get('message', str(e))
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")