import openai
import asyncio
import json
import logging

client = openai.OpenAI()

async def create_assistant_service(data):
    assistant = await asyncio.to_thread(
        client.beta.assistants.create,
        name=data.name,
        instructions=data.instructions,
        tools=data.tools,
        model=data.model
    )
    return assistant

async def upload_file_service(file):
    file_content = await file.read()
    response = await asyncio.to_thread(
        client.files.create,
        file=file_content,
        purpose="assistants"
    )
    return response

async def create_vector_store_service(file_id):
    vector_store = await asyncio.to_thread(
        client.beta.vector_stores.create,
        name="My Vector Store",
        file_ids=[file_id]
    )
    file_batch = await asyncio.to_thread(
        client.beta.vector_stores.file_batches.upload_and_poll,
        vector_store_id=vector_store.id,
        files=[file_id]
    )
    return vector_store, file_batch

async def update_assistant_vector_store_service(assistant_id, vector_store_id):
    assistant = await asyncio.to_thread(
        client.beta.assistants.update,
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
    )
    return assistant

async def create_thread_with_file_service(file, user_message):
    file_content = await file.read()
    message_file = await asyncio.to_thread(
        client.files.create,
        file=file_content,
        purpose="assistants"
    )
    thread = await asyncio.to_thread(
        client.beta.threads.create,
        messages=[
            {
                "role": "user",
                "content": user_message,
                "attachments": [
                    {"file_id": message_file['id'], "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )
    return thread
