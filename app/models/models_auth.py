# models/models_auth.py
from pydantic import BaseModel

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

class VerificationRequest(BaseModel):
    email: str
    code: str