# services/service_o1.py
from openai import OpenAI
from models.models_o1 import O1Request, O1Response
import os

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_o1_completion(request: O1Request) -> O1Response:
    response = client.chat.completions.create(
        model="o1-preview",
        messages=[{"role": "user", "content": request.prompt}]
    )
    completion_text = response.choices[0].message.content.strip()
    return O1Response(completion=completion_text)
