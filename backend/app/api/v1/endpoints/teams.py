from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.team import Team, TeamMember
from app.schemas.team import TeamCreate, TeamInvite, TeamJoin, TeamResponse, TeamMemberResponse
from app.services.team_service import TeamService

router = APIRouter(prefix="/events/{event_id}/teams", tags=["Teams"])

# Standalone team lookup - outside events prefix
standalone_router = APIRouter(prefix="/teams", tags=["Teams"])

@standalone_router.get("/{team_id}", response_model=TeamResponse)
async def get_team_by_id(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    team = await service.team_repo.get_team_with_members(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team

@standalone_router.get("/", response_model=List[TeamResponse])
async def list_my_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Team).join(TeamMember).where(TeamMember.user_id == current_user.id)
    )
    teams = result.scalars().all()
    return teams


@router.get("/", response_model=list[TeamResponse])
async def list_teams(event_id: UUID, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    teams = await service.list_event_teams(event_id)
    return teams


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    event_id: UUID,
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    team = await service.create_team(event_id, team_data, current_user.id)
    return team


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(event_id: UUID, team_id: UUID, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    team = await service.team_repo.get_team_with_members(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


@router.post("/join", response_model=TeamMemberResponse)
async def join_team(
    event_id: UUID,
    join_data: TeamJoin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    member = await service.join_by_code(join_data.invitation_code, current_user.id)
    return member


@router.post("/{team_id}/invite", response_model=TeamMemberResponse)
async def invite_member(
    event_id: UUID,
    team_id: UUID,
    invite_data: TeamInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    member = await service.invite_member(team_id, UUID(invite_data.user_id), current_user.id)
    return member


@router.post("/{team_id}/accept/{member_id}", response_model=TeamMemberResponse)
async def accept_invite(
    event_id: UUID,
    team_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    return await service.accept_invite(team_id, member_id, current_user.id)


@router.post("/{team_id}/reject/{member_id}", response_model=TeamMemberResponse)
async def reject_invite(
    event_id: UUID,
    team_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    return await service.reject_invite(team_id, member_id, current_user.id)


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    event_id: UUID,
    team_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    await service.remove_member(team_id, member_id, current_user.id)


@router.delete("/{team_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_team(
    event_id: UUID,
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TeamService(db)
    await service.leave_team(team_id, current_user.id)
