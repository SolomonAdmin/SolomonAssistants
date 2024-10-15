# services/service_auth.py
import os
import boto3
import hmac
import base64
import hashlib
import jwt
import requests
from botocore.exceptions import ClientError
from models.models_auth import UserSignUp, UserSignIn, TokenResponse, UserResponse, VerificationRequest

class CognitoService:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))
        self.user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = os.getenv('COGNITO_APP_CLIENT_ID')
        self.client_secret = os.getenv('COGNITO_APP_CLIENT_SECRET')

    def get_secret_hash(self, username):
        msg = username + self.client_id
        dig = hmac.new(str(self.client_secret).encode('utf-8'),
                       msg=str(msg).encode('utf-8'),
                       digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    async def sign_up(self, user: UserSignUp) -> UserResponse:
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=user.email,
                Password=user.password,
                UserAttributes=[
                    {'Name': 'name', 'Value': user.name},
                    {'Name': 'email', 'Value': user.email},
                ],
                SecretHash=self.get_secret_hash(user.email)
            )
            return UserResponse(
                id=response['UserSub'],
                email=user.email,
                name=user.name,
            )
        except ClientError as e:
            raise Exception(f"Error signing up user: {str(e)}")

    async def sign_in(self, user: UserSignIn) -> TokenResponse:
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': user.email,
                    'PASSWORD': user.password,
                    'SECRET_HASH': self.get_secret_hash(user.email)
                }
            )
            auth_result = response['AuthenticationResult']
            return TokenResponse(
                access_token=auth_result['AccessToken'],
                id_token=auth_result['IdToken'],
                refresh_token=auth_result['RefreshToken']
            )
        except self.client.exceptions.NotAuthorizedException:
            raise Exception("Incorrect username or password")
        except self.client.exceptions.UserNotFoundException:
            raise Exception("User does not exist")
        except ClientError as e:
            raise Exception(f"Error signing in user: {str(e)}")

    async def get_user(self, access_token: str) -> UserResponse:
        try:
            response = self.client.get_user(AccessToken=access_token)
            user_attrs = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            return UserResponse(
                id=response['Username'],
                email=user_attrs.get('email'),
                name=user_attrs.get('name'),
                solomon_consumer_key=user_attrs.get('custom:solomon_consumer_key')
            )
        except self.client.exceptions.NotAuthorizedException:
            raise Exception("Invalid or expired token")
        except ClientError as e:
            raise Exception(f"Error getting user details: {str(e)}")
        
    async def attach_solomon_consumer_key(self, username: str, solomon_consumer_key: str) -> bool:
        try:
            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[
                    {'Name': 'custom:solomon_consumer_key', 'Value': solomon_consumer_key},
                ]
            )
            return True
        except ClientError as e:
            raise Exception(f"Error attaching Solomon consumer key: {str(e)}")

    async def change_solomon_consumer_key(self, username: str, new_solomon_consumer_key: str) -> bool:
        return await self.attach_solomon_consumer_key(username, new_solomon_consumer_key)

    async def get_solomon_consumer_key(self, username: str) -> str:
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            user_attrs = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            return user_attrs.get('custom:solomon_consumer_key')
        except ClientError as e:
            raise Exception(f"Error getting Solomon consumer key: {str(e)}")
    
    async def confirm_sign_up(self, verification: VerificationRequest) -> bool:
        try:
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=verification.email,
                ConfirmationCode=verification.code,
                SecretHash=self.get_secret_hash(verification.email)
            )
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                raise Exception("Invalid verification code")
            elif error_code == 'ExpiredCodeException':
                raise Exception("Verification code has expired")
            else:
                raise Exception(f"Error confirming sign up: {str(e)}")