from typing import List, Optional
from models.models_assistant_builder_threads import AssistantBuilderThread, AssistantBuilderThreadCreate
from rds_db_connection import DatabaseConnector

class AssistantBuilderThreadService:
    def __init__(self):
        self.db = DatabaseConnector()

    def get_threads(self, solomon_consumer_key: str) -> List[AssistantBuilderThread]:
        threads = self.db.get_assistant_builder_threads(solomon_consumer_key)
        return [AssistantBuilderThread(**thread) for thread in threads]

    def create_thread(self, thread_data: AssistantBuilderThreadCreate) -> bool:
        return self.db.create_assistant_builder_thread(
            thread_data.solomon_consumer_key,
            thread_data.thread_id,
            thread_data.thread_name
        )

    def delete_thread(self, thread_id: str) -> bool:
        return self.db.delete_assistant_builder_thread(thread_id)
    
    def get_assistant_id(self, thread_id: str, solomon_consumer_key: str) -> Optional[str]:
        return self.db.get_assistant_id_by_thread(thread_id, solomon_consumer_key)

    def get_assistant_builder_id(self, solomon_consumer_key: str, workspace_name: str) -> Optional[str]:
        return self.db.get_assistant_builder_id(solomon_consumer_key, workspace_name)