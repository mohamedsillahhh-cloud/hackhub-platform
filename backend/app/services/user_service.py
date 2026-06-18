from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user_by_id(self, user_id: UUID) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_profile(self, user_id: UUID, profile_data: UserUpdate) -> User:
        update_data = profile_data.model_dump(exclude_unset=True)
        user = await self.user_repo.update(user_id, **update_data)
        if not user:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def list_users(
        self,
        page: int = 1,
        size: int = 20,
        role: Optional[UserRole] = None,
        skills: Optional[List[str]] = None,
        university: Optional[str] = None,
        country: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        skip = (page - 1) * size
        return await self.user_repo.list_users_paginated(
            skip=skip,
            limit=size,
            role=role,
            skills=skills,
            university=university,
            country=country,
            search=search,
        )

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        stats = await self.user_repo.get_dashboard_stats()

        from app.models.event import Event
        from sqlalchemy import select, func
        events_count = await self.db.execute(select(func.count(Event.id)))
        stats["events"] = events_count.scalar() or 0

        from app.models.project import Project
        projects_count = await self.db.execute(select(func.count(Project.id)))
        stats["projects"] = projects_count.scalar() or 0

        from app.models.project import ProjectTechnology
        from sqlalchemy import select, func
        techs_result = await self.db.execute(
            select(ProjectTechnology.name, func.count(ProjectTechnology.id).label("count"))
            .group_by(ProjectTechnology.name)
            .order_by(func.count(ProjectTechnology.id).desc())
            .limit(10)
        )
        stats["top_technologies"] = [
            {"name": row.name, "count": row.count}
            for row in techs_result.all()
        ]

        return stats

    async def get_event_stats(self, event_id: UUID) -> Dict[str, Any]:
        from app.models.project import Project
        from app.models.team import Team
        from app.models.evaluation import Evaluation
        from sqlalchemy import select, func

        teams_count = await self.db.execute(
            select(func.count(Team.id)).where(Team.event_id == event_id)
        )
        projects_count = await self.db.execute(
            select(func.count(Project.id)).where(Project.event_id == event_id)
        )
        submitted_count = await self.db.execute(
            select(func.count(Project.id)).where(
                Project.event_id == event_id,
                Project.status.in_(["submitted", "finalized"]),
            )
        )
        evals_count = await self.db.execute(
            select(func.count(Evaluation.id))
            .join(Project, Evaluation.project_id == Project.id)
            .where(Project.event_id == event_id)
        )

        return {
            "event_id": str(event_id),
            "total_teams": teams_count.scalar() or 0,
            "total_projects": projects_count.scalar() or 0,
            "submitted_projects": submitted_count.scalar() or 0,
            "total_evaluations": evals_count.scalar() or 0,
        }
