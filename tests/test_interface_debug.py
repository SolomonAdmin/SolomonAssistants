import asyncio
import argparse
import logging
import traceback
from typing import List, Optional
import os
import sys
import re
import time

# Configure verbose logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Importing WorkatoConfig...")
    from app.services.workato_integration import WorkatoConfig
    print("Importing AssistantBridge...")
    from app.services.assistant_bridge import AssistantBridge
    print("Imports completed successfully")
except Exception as e:
    print(f"Error during imports: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Hard-coded Workato configuration for testing
WORKATO_CONFIG = WorkatoConfig(
    api_token="ad19767e318455a1daa7635b3e5f3ce4055f11376155b45c506ceb4f4f739d1c",
    endpoint_url="https://apim.workato.com/solconsult/assistant-tools-v1/workato-root-tool"
)

async def test_chat(api_key, assistant_id, vector_store_ids=None):
    """Test that chat functionality works."""
    try:
        print("\n=== Testing AssistantBridge ===")
        print("1. Creating bridge instance...")
        bridge = AssistantBridge(api_key, assistant_id, vector_store_ids)
        
        print("2. Initializing bridge...")
        await bridge.initialize(workato_config=WORKATO_CONFIG)
        print("Bridge initialized successfully!")
        
        print("3. Testing chat...")
        response = await bridge.chat("Hello! What can you help me with today?")
        print(f"\nChat response:\n{response}\n")
        
        print("4. Testing streaming chat...")
        print("\nStreaming: ", end="", flush=True)
        async for chunk, event_type in bridge.chat_streaming("Tell me about yourself in 3 sentences."):
            print(chunk, end="", flush=True)
        print("\n\nStreaming completed")
        
        print("5. Getting conversation history...")
        history = bridge.get_conversation_history()
        print(f"Conversation history: {len(history)} messages")
        
        print("Test completed successfully!")
        return True
    except Exception as e:
        print(f"Error during test: {str(e)}")
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Test interface for Assistant Bridge")
    parser.add_argument("api_key", help="OpenAI API key")
    parser.add_argument("assistant_id", help="OpenAI Assistant ID")
    parser.add_argument("--vector-stores", nargs="+", help="Vector store IDs for file search")
    
    args = parser.parse_args()
    
    # Run the test
    success = asyncio.run(test_chat(args.api_key, args.assistant_id, args.vector_stores))
    
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nTests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 