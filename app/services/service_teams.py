from typing import List, Optional
from fastapi import HTTPException
from models.models_teams import TeamCallableAssistant
from rds_db_connection import DatabaseConnector

class TeamService:
    def __init__(self):
        self.db = DatabaseConnector()

    def add_team_member(self, solomon_consumer_key: str, origin_assistant_id: str,
                      callable_assistant_id: str, callable_assistant_reason: Optional[str] = None) -> tuple[bool, str]:
        return self.db.add_team_member(
            solomon_consumer_key=solomon_consumer_key,
            origin_assistant_id=origin_assistant_id,
            callable_assistant_id=callable_assistant_id,
            callable_assistant_reason=callable_assistant_reason
        )

    def get_team_callable_assistants(self, solomon_consumer_key: str, 
                                   origin_assistant_id: str) -> List[TeamCallableAssistant]:
        assistants = self.db.get_team_callable_assistants(
            solomon_consumer_key=solomon_consumer_key,
            origin_assistant_id=origin_assistant_id
        )
        return [TeamCallableAssistant(**assistant) for assistant in assistants]

    def delete_team_callable_assistant(self, solomon_consumer_key: str, origin_assistant_id: str,
                                     callable_assistant_id: str) -> bool:
        return self.db.delete_team_callable_assistant(
            solomon_consumer_key=solomon_consumer_key,
            origin_assistant_id=origin_assistant_id,
            callable_assistant_id=callable_assistant_id
        )