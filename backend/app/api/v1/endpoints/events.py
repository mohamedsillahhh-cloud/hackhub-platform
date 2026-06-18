from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organizer
from app.models.event import EventStatus
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[EventStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    items, total = await service.list_events(
        page=page, size=size, status=status, search=search
    )
    return EventListResponse(items=items, total=total, page=page, size=size)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    service = EventService(db)
    event = await service.create_event(event_data, current_user.id)
    return event


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EventService(db)
    return await service.get_event(event_id)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EventService(db)
    return await service.update_event(event_id, event_data, current_user.id)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EventService(db)
    await service.delete_event(event_id, current_user.id)


@router.patch("/{event_id}/status", response_model=EventResponse)
async def change_event_status(
    event_id: UUID,
    new_status: EventStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EventService(db)
    return await service.change_status(event_id, new_status, current_user.id)
