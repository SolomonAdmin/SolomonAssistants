# utils.py
import os
from dotenv import load_dotenv

# Get the directory of the current file (utils.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the .env file (assuming it's in the parent directory)
dotenv_path = os.path.join(os.path.dirname(current_dir), '.env')

# Load the .env file
load_dotenv(dotenv_path)

# Get the OPENAI_API_KEY from the environment variables
OPENAI_API_KEY_env = os.getenv('OPENAI_API_KEY')

def get_headers(openai_api_key: str = None) -> dict:
    """
    Returns the headers required for OpenAI API requests.
    If openai_api_key is provided, it will use that, otherwise it will use the environment variable.
    """
    api_key = openai_api_key or OPENAI_API_KEY_env
    print(api_key)
    if not api_key:
        raise ValueError("OpenAI API key must be provided either as an argument or set as an environment variable.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    return headers
