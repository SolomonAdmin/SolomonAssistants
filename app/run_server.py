import uvicorn
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Start the WebSocket server for OpenAI Agents")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    print(f"Starting WebSocket server on {args.host}:{args.port}")

    # Determine the correct path to the websocket server
    if os.path.exists(os.path.join(os.path.dirname(__file__), "api", "websocket", "websocket_server.py")):
        server_path = "app.api.websocket.websocket_server:app"
    else:
        server_path = "app.api.websocket_server:app"

    print(f"Using server path: {server_path}")

    uvicorn.run(
        server_path,
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
