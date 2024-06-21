from fastapi import APIRouter, status

router_health_check = APIRouter(tags=["HealthCheck"])

@router_health_check.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "available"}
