# routers/router_o1.py
from fastapi import APIRouter, Depends, HTTPException
from models.models_o1 import O1Request, O1Response
from services.service_o1 import get_o1_completion

router_o1 = APIRouter(
    prefix="/o1",
    tags=["o1-preview"],
)

@router_o1.post("/completion", response_model=O1Response)
async def o1_completion(request: O1Request):
    try:
        response = await get_o1_completion(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))