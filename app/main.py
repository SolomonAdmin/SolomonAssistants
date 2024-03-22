import openai
import time
import requests
import asyncio
import json
import os 
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import logging
from typing import List, Optional, Dict

from fastapi import FastAPI, Query
import asyncio
import json

import sys
from pathlib import Path

# test comments

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))


from assistant_tools import get_stock_price, get_weather_data, send_post_request

# , get_airport_details
from assistant_tools.jiraAgent import jira_run_agent_query

from helpers.aws_helpers import get_secret_value

from tools_config import tools_list

# Set the API key as an environment variable
os.environ["OPENAI_API_KEY"] = get_secret_value("OPENAI_API_KEY")

# Initialize the FastAPI client
app = FastAPI()

# Initialize the OpenAI client comment
client = openai.OpenAI()

@app.get('/')
def read_root():
    return {"message": "Hello, World!!"}

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
@app.post("/list_assistants")
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
    
class ModifyAssistantRequest(BaseModel):
    name: Optional[str] = None
    description: str = ""
    instructions: str = ""
    tools: List[str] = []  # This correctly reflects your current model
    model: str = "gpt-4-1106-preview"
    file_ids: List[str] = []
    metadata: Optional[Dict[str, str]] = None

@app.post("/modify_assistant/{assistant_id}")
async def modify_assistant(assistant_id: str, request: ModifyAssistantRequest):
    try:
        # Directly format the tools array from the request strings
        tools_formatted = [{"type": tool_name} for tool_name in request.tools]

        # Proceed with updating the assistant
        my_updated_assistant = await asyncio.to_thread(
            client.beta.assistants.update,
            assistant_id,
            name=request.name,
            description=request.description,
            instructions=request.instructions,
            tools=tools_formatted,
            model=request.model,
            file_ids=request.file_ids,
            metadata=request.metadata
        )
        return {"message": "Assistant modified successfully", "assistant": my_updated_assistant}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete_assistant/{assistant_id}")
async def delete_assistant(assistant_id: str):
    try:
        response = await asyncio.to_thread(
            client.beta.assistants.delete,
            assistant_id
        )
        return {"message": "Assistant deleted successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete_assistant_file/{assistant_id}/{file_id}")
async def delete_assistant_file(assistant_id: str, file_id: str):
    try:
        deleted_assistant_file = await asyncio.to_thread(
            client.beta.assistants.files.delete,
            assistant_id=assistant_id,
            file_id=file_id
        )
        return {"message": "Assistant file deleted successfully", "response": deleted_assistant_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/retrieve_thread/{thread_id}")
async def retrieve_thread(thread_id: str):
    try:
        my_thread = await asyncio.to_thread(
            client.beta.threads.retrieve,
            thread_id
        )
        return {"message": "Thread retrieved successfully", "thread": my_thread}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ThreadUpdateRequest(BaseModel):
    metadata: Dict[str, str] = Field(
        default={},
        description="Set of key-value pairs for metadata. Keys can be a maximum of 64 characters long and values can be a maximum of 512 characters long."
    )
@app.post("/modify_thread/{thread_id}")
async def modify_thread(thread_id: str, request: ThreadUpdateRequest):
    try:
        my_updated_thread = await asyncio.to_thread(
            client.beta.threads.update,
            thread_id,
            metadata=request.metadata
        )
        return {"message": "Thread modified successfully", "thread": my_updated_thread}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_thread/{thread_id}")
async def delete_thread(thread_id: str):
    try:
        response = await asyncio.to_thread(
            client.beta.threads.delete,
            thread_id
        )
        return {"message": "Thread deleted successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/retrieve_file/{file_id}")
async def retrieve_file(file_id: str):
    try:
        content = await asyncio.to_thread(
            client.files.retrieve_content,
            file_id
        )
        return {"message": "File content retrieved successfully", "content": content}
    except Exception as e:
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
                    output = json.dumps(output)  
                elif func_name == "jira_run_agent_query":
                    # Run synchronous function in a thread pool
                    output = await asyncio.to_thread(
                        jira_run_agent_query,
                        jira_query=arguments['jira_query']
                    )
                    output = json.dumps(output) 
                elif func_name == "send_post_request":
                    # Run synchronous function in a thread pool
                    output = await asyncio.to_thread(
                        send_post_request,
                        data_type=arguments['data_type']
                    )
                    output = json.dumps(output)

                # elif func_name == "get_airport_details":
                #     # Run synchronous function in a thread pool
                #     output = await asyncio.to_thread(
                #         get_airport_details,
                #         airport_code=arguments['airport_code']
                #     )
                #     output_dict = {
                #         'airport_code': str(output)
                #     }
                #     output = json.dumps(output_dict)
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
            await asyncio.sleep(5)  
