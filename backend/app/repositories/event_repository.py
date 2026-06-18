from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.event import Event, EventStatus
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, db: AsyncSession):
        super().__init__(Event, db)

    async def get_by_organizer(self, organizer_id: UUID) -> List[Event]:
        result = await self.db.execute(
            select(Event).where(Event.organizer_id == organizer_id).order_by(Event.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: EventStatus) -> List[Event]:
        result = await self.db.execute(
            select(Event).where(Event.status == status).order_by(Event.start_date.asc())
        )
        return list(result.scalars().all())

    async def get_upcoming(self, limit: int = 10) -> List[Event]:
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Event)
            .where(Event.start_date > now, Event.status == EventStatus.PUBLISHED)
            .order_by(Event.start_date.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active(self) -> List[Event]:
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Event)
            .where(
                and_(
                    Event.start_date <= now,
                    Event.end_date >= now,
                    Event.status.in_([EventStatus.PUBLISHED, EventStatus.IN_PROGRESS]),
                )
            )
            .order_by(Event.start_date.asc())
        )
        return list(result.scalars().all())

    async def list_events(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[EventStatus] = None,
        search: Optional[str] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None,
    ) -> Tuple[List[Event], int]:
        query = select(Event)
        count_query = select(func.count(Event.id))

        if status:
            query = query.where(Event.status == status)
            count_query = count_query.where(Event.status == status)
        if search:
            search_filter = Event.title.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        if start_date_from:
            query = query.where(Event.start_date >= start_date_from)
            count_query = count_query.where(Event.start_date >= start_date_from)
        if start_date_to:
            query = query.where(Event.start_date <= start_date_to)
            count_query = count_query.where(Event.start_date <= start_date_to)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit).order_by(Event.start_date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
