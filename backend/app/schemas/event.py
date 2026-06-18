from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, Field


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
    max_team_size: int = 5
    min_team_size: int = 1


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
    max_team_size: Optional[int] = None
    min_team_size: Optional[int] = None


class EventResponse(BaseModel):
    id: str
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
    organizer_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    size: int
