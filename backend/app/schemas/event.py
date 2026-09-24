from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None
    is_online: bool = False
    regulations: Optional[str] = None
    schedule: Optional[Any] = None
    sponsors: Optional[Any] = None
    prizes: Optional[Any] = None
    faq: Optional[Any] = None
    max_team_size: int = Field(5, ge=1)
    min_team_size: int = Field(1, ge=1)

    @model_validator(mode="after")
    def validate_event_bounds(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        if self.min_team_size > self.max_team_size:
            raise ValueError("min_team_size cannot exceed max_team_size")
        return self


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    is_online: Optional[bool] = None
    regulations: Optional[str] = None
    schedule: Optional[Any] = None
    sponsors: Optional[Any] = None
    prizes: Optional[Any] = None
    faq: Optional[Any] = None
    max_team_size: Optional[int] = Field(None, ge=1)
    min_team_size: Optional[int] = Field(None, ge=1)


class EventResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None
    is_online: bool
    status: str
    regulations: Optional[str] = None
    schedule: Optional[Any] = None
    sponsors: Optional[Any] = None
    prizes: Optional[Any] = None
    faq: Optional[Any] = None
    max_team_size: int
    min_team_size: int
    organizer_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    size: int
