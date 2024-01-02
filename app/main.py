import openai
import time
import yfinance as yf
import requests
import asyncio
import json
import os 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from fastapi import FastAPI
import asyncio
import json

from typing import Union, Optional
from dotenv import load_dotenv

import sys
from pathlib import Path

# Load .env file if exists
load_dotenv()

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))

from tools import get_stock_price, get_weather_data
from tools_config import tools_list

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the FastAPI client
app = FastAPI()

# Initialize the OpenAI client
client = openai.OpenAI()

class AssistantData(BaseModel):
    name: str
    instructions: str

@app.post("/create_assistant")
async def create_assistant(assistant_data: AssistantData):
    try:
        logging.info(f"Creating assistant with name: {assistant_data.name} and instructions: {assistant_data.instructions}")
        assistant = client.beta.assistants.create(
            name=assistant_data.name,
            instructions=assistant_data.instructions,
            tools=tools_list,
            model="gpt-4-1106-preview",
        )
        return {"message": "Assistant created successfully", "assistant": assistant}
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# POST endpoint to create a thread
@app.post("/create_thread")
async def create_thread():
    try:
        thread = client.beta.threads.create()
        return {"message": "Thread created successfully", "thread": thread}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-assistant/")
async def run_assistant(thread_id: str, assistant_id: str, content: str):
    # Add a message to a thread in a thread pool
    message = await asyncio.to_thread(
        client.beta.threads.messages.create,
        thread_id=thread_id,
        role="user",
        content=content
    )
    
@app.post("/list_assistants/")
async def list_assistants():
    try:
        my_assistants = await asyncio.to_thread(
            client.beta.assistants.list,
            order="desc"
        )
        return {"assistants": my_assistants.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Run the assistant in a thread pool
    run = await asyncio.to_thread(
        client.beta.threads.runs.create,
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user."
    )

    # Check run status
    while True:
        await asyncio.sleep(5)  # Non-blocking sleep
        run_status = await asyncio.to_thread(
            client.beta.threads.runs.retrieve,
            thread_id=thread_id,
            run_id=run.id
        )

        if run_status.status == 'completed':
            messages = await asyncio.to_thread(
                client.beta.threads.messages.list, 
                thread_id=thread_id
            )
            return {"messages": messages.data}

        elif run_status.status == 'requires_action':
            print("Function Calling")
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            print(required_actions)
            tool_outputs = []

            for action in required_actions["tool_calls"]:
                func_name = action['function']['name']
                arguments = json.loads(action['function']['arguments'])

                if func_name == "get_stock_price":
                    # Run synchronous function in a thread pool
                    output = await asyncio.to_thread(
                        get_stock_price,
                        symbol=arguments['symbol']
                    )
                elif func_name == "get_weather_data":
                    # Run synchronous function in a thread pool
                    output = await asyncio.to_thread(
                        get_weather_data,
                        location=arguments['location']
                    )
                    output = json.dumps(output)  # Convert dictionary to JSON string
                else:
                    raise ValueError(f"Unknown function: {func_name}")

                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })

            print("Submitting outputs back to the Assistant...")
            await asyncio.to_thread(
                client.beta.threads.runs.submit_tool_outputs,
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        else:
            print("Waiting for the Assistant to process...")
            await asyncio.sleep(5)  # Non-blocking sleep
