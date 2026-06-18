from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TeamInvite(BaseModel):
    user_id: str


class TeamJoin(BaseModel):
    invitation_code: str


class TeamMemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    role: str
    status: str
    invited_by: Optional[str] = None
    created_at: datetime
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    event_id: str
    leader_id: str
    invitation_code: str
    created_at: datetime
    updated_at: datetime
    members: List[TeamMemberResponse] = []

    model_config = {"from_attributes": True}
