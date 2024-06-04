# utils.py
import os

def get_headers(openai_api_key: str = None) -> dict:
    """
    Returns the headers required for OpenAI API requests.
    If openai_api_key is provided, it will use that, otherwise it will use the environment variable.
    """
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided either as an argument or set as an environment variable.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    return headers
