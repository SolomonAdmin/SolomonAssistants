#!/usr/bin/env python
import asyncio
import websockets
import json
import sys
import argparse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_client(solomon_consumer_key, assistant_id, vector_store_ids=None):
    """Test the WebSocket API with streaming responses."""
    uri = "ws://localhost:8000/ws"
    print(f"Connecting to {uri}...")
    
    async with websockets.connect(uri) as websocket:
        # Send connection parameters
        await websocket.send(json.dumps({
            "solomon_consumer_key": solomon_consumer_key,
            "assistant_id": assistant_id,
            "vector_store_ids": vector_store_ids
        }))
        
        # Wait for ready message
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Server: {response}")
        
        if response_data.get("type") == "error":
            print(f"Error: {response_data.get('error')}")
            return
        
        # Start interactive mode
        print("\n=== Interactive WebSocket Test ===")
        print("Type your messages, or 'exit' to quit")
        
        while True:
            # Get user input
            user_input = input("You: ")
            
            if user_input.lower() == "exit":
                break
            
            # Send message to server
            await websocket.send(json.dumps({
                "type": "message",
                "content": user_input,
                "stream": True  # Enable streaming
            }))
            
            # Process server responses
            assistant_response = ""
            print("Assistant: ", end="", flush=True)
            
            while True:
                try:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "stream":
                        # Print streaming content
                        print(response_data.get("content", ""), end="", flush=True)
                        assistant_response += response_data.get("content", "")
                    elif response_data.get("type") == "tool":
                        # Print tool usage
                        if response_data.get("tool") == "call":
                            print(f"\n[Using tool: {response_data.get('name', 'unknown')}]", end="", flush=True)
                        elif response_data.get("tool") == "output":
                            print(f"\n[Tool output: {response_data.get('content', '')}]", end="", flush=True)
                    elif response_data.get("type") == "completion":
                        # Stream complete
                        print()  # Add newline
                        break
                    elif response_data.get("type") == "error":
                        # Error occurred
                        print(f"\nError: {response_data.get('error')}")
                        break
                    elif response_data.get("type") == "system":
                        # System message
                        if "Processing" not in response_data.get("message", ""):
                            print(f"\nSystem: {response_data.get('message')}")
                    elif response_data.get("type") == "response":
                        # Non-streaming response
                        print(response_data.get("content", ""))
                        break
                except Exception as e:
                    logger.error(f"Error in WebSocket communication: {str(e)}")
                    print(f"\nConnection error: {str(e)}")
                    return

def main():
    parser = argparse.ArgumentParser(description="Test the WebSocket API")
    parser.add_argument("solomon_consumer_key", help="Solomon Consumer Key")
    parser.add_argument("assistant_id", help="OpenAI Assistant ID")
    parser.add_argument("--vector-stores", nargs="+", help="Vector store IDs for file search")

    args = parser.parse_args()

    try:
        asyncio.run(test_websocket_client(args.solomon_consumer_key, args.assistant_id, args.vector_stores))
    except KeyboardInterrupt:
        print("\nTest terminated by user")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()