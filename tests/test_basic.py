import asyncio
import argparse
import logging
import sys
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import AsyncOpenAI

async def direct_assistant_test(api_key, assistant_id):
    """Test the assistant directly using OpenAI API."""
    print("Starting direct assistant test...")
    
    # Initialize the OpenAI client
    client = AsyncOpenAI(api_key=api_key)
    
    # Create a thread
    thread = await client.beta.threads.create()
    print(f"Created thread: {thread.id}")
    
    # Add a message to the thread
    message = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello! How are you today?"
    )
    print(f"Added message to thread")
    
    # Run the assistant
    run = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    print(f"Started run: {run.id}")
    
    # Wait for the run to complete
    while True:
        run_status = await client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"Run status: {run_status.status}")
        
        if run_status.status == "completed":
            break
        elif run_status.status in ["failed", "cancelled", "expired"]:
            print(f"Run failed with status: {run_status.status}")
            return
        
        # Wait before checking again
        await asyncio.sleep(1)
    
    # Get the messages
    messages = await client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    # Print the assistant's response
    print("\nAssistant's response:")
    for msg in messages.data:
        if msg.role == "assistant":
            for content_item in msg.content:
                if content_item.type == "text":
                    print(content_item.text.value)
    
    print("\nTest completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Basic test for OpenAI Assistant")
    parser.add_argument("api_key", help="OpenAI API key")
    parser.add_argument("assistant_id", help="OpenAI Assistant ID")
    
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(direct_assistant_test(args.api_key, args.assistant_id))

if __name__ == "__main__":
    main() 