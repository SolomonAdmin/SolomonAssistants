# models/models_auth.py
from pydantic import BaseModel
from typing import Optional

class UserSignUp(BaseModel):
    email: str
    password: str
    name: str

class UserSignIn(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    solomon_consumer_key: Optional[str] = None

class VerificationRequest(BaseModel):
    email: str
    code: str

class SolomonConsumerKeyUpdate(BaseModel):
    solomon_consumer_key: str