import openai
import time
import yfinance as yf
import requests
import asyncio
import json
import os 
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import logging
from typing import List, Optional, Dict

from fastapi import FastAPI, Query
import asyncio
import json

import sys
from pathlib import Path

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))

from tools import get_stock_price, get_weather_data
from tools.jiraAgent import jira_run_agent_query
from helpers.aws_helpers import get_secret_value

from tools_config import tools_list

# Set the API key as an environment variable
os.environ["OPENAI_API_KEY"] = get_secret_value("OPENAI_API_KEY")

# Initialize the FastAPI client
app = FastAPI()

# Initialize the OpenAI client
client = openai.OpenAI()

class AssistantData(BaseModel):
    model: str = "gpt-4-1106-preview"
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[str]] = []
    file_ids: Optional[List[str]] = []
    metadata: Optional[Dict[str, str]] = {}

@app.post("/create_assistant")
async def create_assistant(assistant_data: AssistantData):
    try:
        logging.info(f"Creating assistant with model: {assistant_data.model}")
        assistant = client.beta.assistants.create(
            name=assistant_data.name,
            instructions=assistant_data.instructions,
            tools=assistant_data.tools or tools_list, 
            model=assistant_data.model,  # Use the model from the request data
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

# POST endpoint to list assistants
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
    
@app.post("/upload_file_for_assistants")
async def upload_file_for_assistants(file: UploadFile = File(...)):
    try:
        # Read file content
        file_content = await file.read()

        # Upload the file to OpenAI
        response = await asyncio.to_thread(
            client.files.create,
            file=file_content,
            purpose="assistants"
        )

        return {"message": "File uploaded successfully", "response": response}

    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# POST endpoint to run assistant with a thread
@app.post("/run-assistant/")
async def run_assistant(thread_id: str, assistant_id: str, content: str, file_ids: Optional[List[str]] = Query(default=None)):
    # Add a message to a thread in a thread pool
    message = await asyncio.to_thread(
        client.beta.threads.messages.create,
        thread_id=thread_id,
        role="user",
        content=content,
        file_ids=file_ids if file_ids else []
    )

    # Run the assistant in a thread pool
    run = await asyncio.to_thread(
        client.beta.threads.runs.create,
        thread_id=thread_id,
        assistant_id=assistant_id
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
                elif func_name == "jira_run_agent_query":
                    # Run synchronous function in a thread pool
                    output = await asyncio.to_thread(
                        jira_run_agent_query,
                        jira_query=arguments['jira_query']
                    )
                    output = json.dumps(output)  # Convert dictionary to JSON string, if necessary
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
