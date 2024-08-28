from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from pydantic import BaseModel
import os
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import os

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sign up
class UserSignUp(BaseModel):
    email: EmailStr
    password: str

async def sign_up_user(user: UserSignUp):
    # Attempt to create a new user
    response = supabase.auth.sign_up({
        "email": user.email,
        "password": user.password
    })
    print(response)
    # Check for errors in the response
    if response.get('error'):
        raise HTTPException(status_code=400, detail=response['error']['message'])
    
    if not response or not response.user:
        return {'status': 'error', 'message': 'User creation failed'}
    
    return response['user']

# Sign in
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    email: str
    password: str

async def authenticate_user(user: User):
    response = supabase.auth.sign_in_with_password(email=user.email, password=user.password)
    if response.get('error'):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return response['user']

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user
