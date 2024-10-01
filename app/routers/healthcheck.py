# routers/healthcheck.py

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.service_healthcheck import HealthcheckService

router_health_check = APIRouter(tags=["HealthCheck"])

class HealthResponse(BaseModel):
    status: str

class DatabaseHealthResponse(BaseModel):
    status: str
    message: str

@router_health_check.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    operation_id="health_check",
    response_model=HealthResponse
)
async def health_check():
    return {"status": "available"}

@router_health_check.get(
    "/db",
    status_code=status.HTTP_200_OK,
    operation_id="db_health_check",
    response_model=DatabaseHealthResponse
)
async def db_health_check():
    is_healthy, message = await HealthcheckService.check_database_connection()
    if is_healthy:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "available", "message": message}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "message": message}
        )