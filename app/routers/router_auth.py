# routers/router_auth.py
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer
from models.models_auth import UserSignUp, UserSignIn, TokenResponse, UserResponse, VerificationRequest, SolomonConsumerKeyUpdate
from services.service_auth import CognitoService
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

router_auth = APIRouter(tags=["Auth"])
cognito_service = CognitoService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# Dependency to get the token
async def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return credentials.credentials

@router_auth.post("/signup", response_model=UserResponse)
async def sign_up(user: UserSignUp):
    try:
        return await cognito_service.sign_up(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_auth.post("/signin", response_model=TokenResponse)
async def sign_in(user: UserSignIn):
    try:
        return await cognito_service.sign_in(user)
    except Exception as e:
        if "Incorrect username or password" in str(e):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        elif "User does not exist" in str(e):
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        return await cognito_service.get_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")
    return token

@router_auth.get("/me", response_model=UserResponse)
async def get_user_info(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    try:
        user = await cognito_service.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router_auth.post("/verify")
async def verify_signup(verification: VerificationRequest):
    try:
        result = await cognito_service.confirm_sign_up(verification)
        if result:
            return {"message": "User verified successfully"}
    except Exception as e:
        if "Invalid verification code" in str(e):
            raise HTTPException(status_code=400, detail="Invalid verification code")
        elif "Verification code has expired" in str(e):
            raise HTTPException(status_code=400, detail="Verification code has expired")
        else:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router_auth.put("/solomon-consumer-key")
async def update_solomon_consumer_key(
    update: SolomonConsumerKeyUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        result = await cognito_service.change_solomon_consumer_key(current_user.email, update.solomon_consumer_key)
        if result:
            return {"message": "Solomon consumer key updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router_auth.get("/solomon-consumer-key")
async def get_solomon_consumer_key(current_user: UserResponse = Depends(get_current_user)):
    try:
        consumer_key = await cognito_service.get_solomon_consumer_key(current_user.email)
        return {"solomon_consumer_key": consumer_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")