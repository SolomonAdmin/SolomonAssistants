from pydantic import BaseModel
from typing import Optional

class Thread(BaseModel):
    thread_id: str
    thread_name: Optional[str] = None

class ThreadsResponse(BaseModel):
    threads: list[Thread]