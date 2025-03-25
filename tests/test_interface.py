import asyncio
import argparse
import logging
from typing import List, Optional
import os
import sys
import re
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

# Print Python path to help diagnose import issues
print("Python path:")
for path in sys.path:
    print(f"  {path}")

# Print Python version
print(f"Python version: {sys.version}")

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.assistant_bridge import AssistantBridge
from app.services.workato_integration import WorkatoConfig

# Configure logging - set to WARNING to suppress INFO logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Also suppress httpx logging
logging.getLogger("httpx").setLevel(logging.WARNING)

# Hard-coded Workato configuration for testing
WORKATO_CONFIG = WorkatoConfig(
    api_token="ad19767e318455a1daa7635b3e5f3ce4055f11376155b45c506ceb4f4f739d1c",
    endpoint_url="https://apim.workato.com/solconsult/assistant-tools-v1/workato-root-tool"
)

def format_response_with_citations(response: str) -> str:
    """Format the response to highlight web search citations."""
    # Check if the response contains markdown-style links
    if "[" in response and "](" in response:
        # Add a separator before the citations section if it exists
        if "##" in response:
            parts = response.split("##")
            main_content = parts[0]
            citations = "##" + "##".join(parts[1:])
            
            # Format the main content
            formatted_main = format_markdown_links(main_content)
            
            # Format the citations section
            formatted_citations = format_markdown_links(citations)
            
            return formatted_main + "\n" + formatted_citations
        else:
            return format_markdown_links(response)
    else:
        return response

def format_markdown_links(text):
    """Format markdown links to make them more visible."""
    # Find all markdown links [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    # Replace with a formatted version
    formatted = re.sub(pattern, r'[\1](\2)', text)
    
    return formatted

async def interactive_chat(api_key, assistant_id, vector_store_ids=None):
    """Run an interactive chat session with the assistant."""
    print("\n=== Assistant Bridge Test Interface ===")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    print("Type 'history' to see the conversation history.")
    print("Type 'clear' to clear the conversation history.")
    print("Type 'stream' to toggle streaming mode.")
    print("=========================================\n")
    
    # Initialize the bridge
    print("Initializing bridge...")
    bridge = AssistantBridge(api_key, assistant_id, vector_store_ids)
    await bridge.initialize(workato_config=WORKATO_CONFIG)
    print("Bridge initialized successfully!\n")
    print("NOTE: This interface now uses OpenAIResponsesModel by default for all interactions.")
    print("      Web search capability is enabled and will be used when appropriate.")
    print("      Workato integration is enabled for system interactions.")
    
    # Print file search status
    if vector_store_ids:
        print(f"      File search capability is enabled with vector stores: {vector_store_ids}")
    else:
        print("      File search capability is disabled (no vector stores provided).")
    print()
    
    # Stream mode flag
    streaming_enabled = True
    print(f"Streaming mode is {'enabled'} by default.")

    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for chatting! Goodbye.")
            break
            
        # Check for history command
        elif user_input.lower() == "history":
            history = bridge.get_conversation_history()
            print("\n=== Conversation History ===")
            for entry in history:
                role = entry["role"].upper()
                content = entry["content"]
                print(f"{role}: {content}\n")
            continue
            
        # Check for clear command
        elif user_input.lower() == "clear":
            bridge.clear_history()
            print("\nConversation history cleared.\n")
            continue
        
        # Toggle streaming mode
        elif user_input.lower() == "stream":
            streaming_enabled = not streaming_enabled
            print(f"\nStreaming mode is now {'enabled' if streaming_enabled else 'disabled'}.\n")
            continue
        
        # Process the user message
        print("\nAssistant is thinking...")
        try:
            # Use streaming or non-streaming mode based on user preference
            if streaming_enabled:
                # Use streaming mode - display tokens as they come
                full_response = ""
                tool_used = False
                print("\nAssistant: ", end="", flush=True)
                
                async for chunk, event_type in bridge.chat_streaming(user_input):
                    if event_type == "raw_response" or event_type == "message":
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    elif event_type == "tool_call":
                        # Print tool usage without adding to full response
                        time.sleep(0.1)  # Brief pause for readability
                        print(f"\n[{chunk}]", end="", flush=True)
                        tool_used = True
                    elif event_type == "tool_output":
                        # Print tool result without adding to full response
                        time.sleep(0.1)  # Brief pause for readability
                        print(f"\n[{chunk}]", end="", flush=True)
                
                # Format the complete response at the end
                formatted_response = format_response_with_citations(full_response)
                print("\n")  # Add an extra line break after streaming
                
                # Check if the response likely contains web search results
                if "[" in full_response and "](" in full_response:
                    print("(Web search was used to generate this response)\n")
                elif tool_used:
                    print("(Tools were used to generate this response)\n")
            else:
                # Use non-streaming mode - display complete response at once
                response = await bridge.chat(user_input)
                
                # Format the response to highlight citations
                formatted_response = format_response_with_citations(response)
                print(f"\nAssistant: {formatted_response}\n")
                
                # Check if the response likely contains web search results
                if "[" in response and "](" in response:
                    print("(Web search was used to generate this response)\n")

        except Exception as e:
            print(f"\nError: {str(e)}\n")

def main():
    parser = argparse.ArgumentParser(description="Test interface for Assistant Bridge")
    parser.add_argument("api_key", help="OpenAI API key")
    parser.add_argument("assistant_id", help="OpenAI Assistant ID")
    parser.add_argument("--vector-stores", nargs="+", help="Vector store IDs for file search")
    
    args = parser.parse_args()
    
    # Run the interactive chat
    asyncio.run(interactive_chat(args.api_key, args.assistant_id, args.vector_stores))

if __name__ == "__main__":
    main() 