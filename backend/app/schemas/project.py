from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    challenge_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    github_url: Optional[str] = None
    demo_video_url: Optional[str] = None
    presentation_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[str] = None
    demo_video_url: Optional[str] = None
    presentation_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    challenge_id: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    team_id: str
    event_id: str
    challenge_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    github_url: Optional[str] = None
    demo_video_url: Optional[str] = None
    presentation_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    status: str
    submitted_at: Optional[datetime] = None
    updated_at: datetime

    model_config = {"from_attributes": True}
