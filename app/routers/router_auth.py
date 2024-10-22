# routers/router_auth.py
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer
from models.models_auth import UserSignUp, UserSignIn, TokenResponse, UserResponse, VerificationRequest, SolomonConsumerKeyUpdate
from services.service_auth import CognitoService
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from botocore.exceptions import ClientError
from rds_db_connection import DatabaseConnector 
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

router_auth = APIRouter(tags=["Auth"])
cognito_service = CognitoService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()
db_connector = DatabaseConnector()  

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
        # Step 1: Retrieve user data from Cognito
        cognito_user = await cognito_service.get_user(token)
        
        # Step 2: Fetch Solomon consumer key from the database
        solomon_consumer_key = db_connector.get_consumer_key_by_email(cognito_user.email)
        
        # Step 3: Combine the data and create the final response
        user_response = UserResponse(
            id=cognito_user.id,
            email=cognito_user.email,
            name=cognito_user.name,
            solomon_consumer_key=solomon_consumer_key
        )
        
        return user_response
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
        
@router_auth.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Query(...), email: str = Query(...)):
    try:
        token_response = await cognito_service.refresh_token(refresh_token, email)
        return token_response
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router_auth.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        cognito_service.client.global_sign_out(AccessToken=token)
        return {"message": "Logged out successfully"}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error logging out: {str(e)}")
    
@router_auth.get("/consumer-key", response_model=dict)
async def get_consumer_key(
    authorization: str = Header(...),
):
    """
    Get the solomon consumer key for the authenticated user.
    Requires Bearer token authentication.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        # Step 1: Validate token and get user from Cognito
        cognito_user = await cognito_service.get_user(token)
        
        # Step 2: Get consumer key from RDS
        consumer_key = db_connector.get_consumer_key_by_email(cognito_user.email)
        
        if consumer_key is None:
            logger.warning(f"No consumer key found for user: {cognito_user.email}")
            raise HTTPException(status_code=404, detail="Consumer key not found")
            
        return {"solomon_consumer_key": consumer_key}
        
    except Exception as e:
        logger.error(f"Error retrieving consumer key: {str(e)}")
        if "Invalid or expired token" in str(e):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router_auth.put("/consumer-key")
async def update_consumer_key(
    update: SolomonConsumerKeyUpdate,
    authorization: str = Header(...),
):
    """
    Update the solomon consumer key for the authenticated user in RDS database.
    Requires Bearer token authentication.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        # Step 1: Validate token and get user from Cognito
        cognito_user = await cognito_service.get_user(token)
        logger.info(f"Updating consumer key for user: {cognito_user.email}")
        
        # Step 2: Update consumer key in RDS
        success = db_connector.update_solomon_consumer_key(
            cognito_user.email, 
            update.solomon_consumer_key
        )
        
        if not success:
            logger.warning(f"Failed to update consumer key for user: {cognito_user.email}")
            raise HTTPException(
                status_code=404,
                detail="User not found in database or update failed"
            )
            
        logger.info(f"Successfully updated consumer key for user: {cognito_user.email}")
        return {
            "message": "Solomon consumer key updated successfully",
            "email": cognito_user.email
        }
        
    except Exception as e:
        logger.error(f"Error updating consumer key: {str(e)}")
        if "Invalid or expired token" in str(e):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")