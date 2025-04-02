"""
OpenAI Responses Model implementation.
"""
from typing import Any, AsyncGenerator
from openai import AsyncOpenAI

class OpenAIResponsesModel:
    """OpenAI model using the responses API."""
    
    def __init__(self, openai_client: AsyncOpenAI, model: str = "gpt-4"):
        self.client = openai_client
        self.model = model
    
    async def generate(self, prompt: str) -> str:
        """Generate a response using the OpenAI API."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the OpenAI API."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content 