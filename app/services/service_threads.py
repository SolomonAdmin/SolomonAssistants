from typing import List
from models.models_threads import Thread
from rds_db_connection import DatabaseConnector

class ThreadService:
    def __init__(self):
        self.db = DatabaseConnector()

    def get_threads(self, solomon_consumer_key: str) -> List[Thread]:
        threads = self.db.get_threads(solomon_consumer_key)
        return [Thread(**thread) for thread in threads]