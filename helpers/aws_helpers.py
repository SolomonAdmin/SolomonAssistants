import boto3
from botocore.exceptions import ClientError
import json

from config import Settings, get_settings

settings: Settings = get_settings()

def get_secret_value(key_name: str):
    secret_name = settings.aws_secret_name
    region_name = settings.aws_default_region

    # Create a Secrets Manager client
    session = boto3.session.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=region_name
    )
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # Log and re-raise the exception
        print(f"Error fetching secret: {e}")
        raise e

    # Parse the secret value
    secret = get_secret_value_response['SecretString']
    
    # Convert the secret string to a dictionary
    secret_dict = json.loads(secret)

    # Return the value associated with the provided key
    return secret_dict.get(key_name)