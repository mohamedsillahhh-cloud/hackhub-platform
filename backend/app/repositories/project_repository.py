from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_by_event(self, event_id: UUID) -> List[Project]:
        result = await self.db.execute(
            select(Project).where(Project.event_id == event_id).order_by(Project.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_team(self, team_id: UUID) -> Optional[Project]:
        result = await self.db.execute(
            select(Project).where(Project.team_id == team_id)
        )
        return result.scalar_one_or_none()

    async def get_submitted(self, event_id: UUID) -> List[Project]:
        result = await self.db.execute(
            select(Project).where(
                Project.event_id == event_id,
                Project.status.in_([ProjectStatus.SUBMITTED, ProjectStatus.FINALIZED]),
            )
        )
        return list(result.scalars().all())

    async def search(self, event_id: UUID, query: str) -> Tuple[List[Project], int]:
        search_filter = or_(
            Project.name.ilike(f"%{query}%"),
            Project.description.ilike(f"%{query}%"),
        )
        count_result = await self.db.execute(
            select(func.count(Project.id)).where(Project.event_id == event_id, search_filter)
        )
        total = count_result.scalar() or 0
        result = await self.db.execute(
            select(Project).where(Project.event_id == event_id, search_filter).order_by(Project.updated_at.desc())
        )
        return list(result.scalars().all()), total
