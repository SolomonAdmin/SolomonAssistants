import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router
from routers.healthcheck import router_health_check
from fastapi.responses import Response
import yaml
import functools

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))

from helpers.aws_helpers import get_secret_value

# Set environment variables
os.environ["AWS_SECRET_ACCESS_KEY"] = get_secret_value("AWS_SECRET_ACCESS_KEY")
os.environ["AWS_ACCESS_KEY_ID"] = get_secret_value("AWS_ACCESS_KEY_ID")

# Initialize the FastAPI application
app = FastAPI(title="OpenAPI Assistants V2.0", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router_health_check)
app.include_router(router)

# Optional: Customize OpenAPI schema
@app.on_event("startup")
async def startup_event():
    openapi_schema = app.openapi()
    # print(openapi_schema)
    app.openapi_schema = openapi_schema

@app.get("/openapi.yaml")
@functools.lru_cache()
def get_openapi_yaml() -> Response:
    openapi_json = app.openapi()  # Get the OpenAPI JSON spec
    yaml_output = yaml.dump(openapi_json)  # Convert JSON to YAML
    return Response(content=yaml_output, media_type="text/x-yaml")

# # Optional: Add a root endpoint
# @app.get("/")
# async def root():
#     return {"message": "Welcome to the API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)