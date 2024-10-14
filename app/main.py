import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from router import router
from routers.healthcheck import router_health_check
from fastapi.responses import Response
import yaml
import functools

# Add the parent directory to sys.path to make 'tools' module discoverable
sys.path.append(str(Path(__file__).parent.parent))

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

# Customize OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OpenAPI Assistants V2.0",
        version="0.1.0",
        description="Your API description",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/openapi.yaml")
@functools.lru_cache()
def get_openapi_yaml() -> Response:
    openapi_json = app.openapi()  # Get the OpenAPI JSON spec
    yaml_output = yaml.dump(openapi_json)  # Convert JSON to YAML
    return Response(content=yaml_output, media_type="text/x-yaml")

# Debug middleware to log requests
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Received request: {request.method} {request.url}")
    print("Headers:")
    for name, value in request.headers.items():
        print(f"{name}: {value}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)