# models/models_o1.py
from pydantic import BaseModel

class O1Request(BaseModel):
    prompt: str

class O1Response(BaseModel):
    completion: str
