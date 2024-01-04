import boto3
from botocore.exceptions import ClientError
import json

def get_secret_value(key_name: str):

    secret_name = "prod/SolomonAssistantsApp"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

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