from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventStatus
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = EventRepository(db)

    VALID_TRANSITIONS = {
        EventStatus.DRAFT: [EventStatus.PUBLISHED],
        EventStatus.PUBLISHED: [EventStatus.IN_PROGRESS, EventStatus.DRAFT],
        EventStatus.IN_PROGRESS: [EventStatus.CLOSED],
        EventStatus.CLOSED: [],
    }

    async def create_event(self, event_data: EventCreate, organizer_id: UUID) -> Event:
        return await self.event_repo.create(
            title=event_data.title,
            description=event_data.description,
            cover_image=event_data.cover_image,
            start_date=event_data.start_date,
            end_date=event_data.end_date,
            location=event_data.location,
            is_online=event_data.is_online,
            regulations=event_data.regulations,
            schedule=event_data.schedule,
            sponsors=event_data.sponsors,
            prizes=event_data.prizes,
            faq=event_data.faq,
            max_team_size=event_data.max_team_size,
            min_team_size=event_data.min_team_size,
            organizer_id=organizer_id,
        )

    async def update_event(self, event_id: UUID, event_data: EventUpdate, user_id: UUID) -> Event:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        if event.organizer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this event")

        update_data = event_data.model_dump(exclude_unset=True)
        updated = await self.event_repo.update(event_id, **update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return updated

    async def delete_event(self, event_id: UUID, user_id: UUID) -> None:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        if event.organizer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this event")
        await self.event_repo.delete(event_id)

    async def get_event(self, event_id: UUID) -> Event:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return event

    async def list_events(
        self,
        page: int = 1,
        size: int = 20,
        status: Optional[EventStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Event], int]:
        skip = (page - 1) * size
        return await self.event_repo.list_events(
            skip=skip,
            limit=size,
            status=status,
            search=search,
        )

    async def change_status(self, event_id: UUID, new_status: EventStatus, user_id: UUID) -> Event:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        if event.organizer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to change event status")

        allowed = self.VALID_TRANSITIONS.get(event.status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {event.status.value} to {new_status.value}",
            )

        updated = await self.event_repo.update(event_id, status=new_status)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return updated
