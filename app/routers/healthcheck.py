from fastapi import APIRouter, status
from pydantic import BaseModel

router_health_check = APIRouter(tags=["HealthCheck"])

class HealthResponse(BaseModel):
    status: str

@router_health_check.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    operation_id="health_check",
    response_model=HealthResponse
)
async def health_check():
    return {"status": "available"}