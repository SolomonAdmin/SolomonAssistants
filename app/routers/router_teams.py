from fastapi import APIRouter, HTTPException, Header, Depends, Path
from models.models_teams import TeamMemberCreate, TeamCallableAssistantsResponse
from services.service_teams import TeamService

router_teams = APIRouter(prefix="/teams", tags=["Teams"])

@router_teams.post("/member/{origin_assistant_id}")
async def add_team_member(
    team_member_data: TeamMemberCreate,
    origin_assistant_id: str = Path(..., description="ID of the origin assistant"),
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    team_service: TeamService = Depends(TeamService)
):
    success, message = team_service.add_team_member(
        solomon_consumer_key=solomon_consumer_key,
        origin_assistant_id=origin_assistant_id,
        callable_assistant_id=team_member_data.callable_assistant_id,
        callable_assistant_reason=team_member_data.callable_assistant_reason
    )
    
    if not success:
        if "already exists" in message:
            raise HTTPException(status_code=409, detail=message)  # 409 Conflict
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}

@router_teams.get("/callable-assistants/{origin_assistant_id}", response_model=TeamCallableAssistantsResponse)
async def get_team_callable_assistants(
    origin_assistant_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    team_service: TeamService = Depends(TeamService)
):
    callable_assistants = team_service.get_team_callable_assistants(
        solomon_consumer_key=solomon_consumer_key,
        origin_assistant_id=origin_assistant_id
    )
    return TeamCallableAssistantsResponse(callable_assistants=callable_assistants)

@router_teams.delete("/callable-assistant/{origin_assistant_id}/{callable_assistant_id}")
async def delete_team_callable_assistant(
    origin_assistant_id: str,
    callable_assistant_id: str,
    solomon_consumer_key: str = Header(..., description="Solomon Consumer Key for authentication"),
    team_service: TeamService = Depends(TeamService)
):
    success = team_service.delete_team_callable_assistant(
        solomon_consumer_key=solomon_consumer_key,
        origin_assistant_id=origin_assistant_id,
        callable_assistant_id=callable_assistant_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Team callable assistant not found")
    
    return {"message": "Team callable assistant deleted successfully"}