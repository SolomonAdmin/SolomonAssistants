from pydantic import BaseModel
from typing import Optional

class AssistantBuilderThread(BaseModel):
    thread_id: str
    thread_name: str

class AssistantBuilderThreadCreate(BaseModel):
    solomon_consumer_key: str
    thread_id: str
    thread_name: str

class AssistantBuilderThreadsResponse(BaseModel):
    threads: list[AssistantBuilderThread]