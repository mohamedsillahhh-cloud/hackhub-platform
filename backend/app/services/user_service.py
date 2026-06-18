from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User, UserRole
from app.models.event import Event
from app.models.project import Project
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
        user_stats = await self.user_repo.get_dashboard_stats()

        events_total = await self.db.execute(select(func.count(Event.id)))
        events_published = await self.db.execute(
            select(func.count(Event.id)).where(Event.status == "published")
        )
        events_in_progress = await self.db.execute(
            select(func.count(Event.id)).where(Event.status == "in_progress")
        )
        events_closed = await self.db.execute(
            select(func.count(Event.id)).where(Event.status == "closed")
        )

        projects_total = await self.db.execute(select(func.count(Project.id)))
        teams_total = await self.db.execute(select(func.count(Project.id)))

        recent_events_result = await self.db.execute(
            select(Event).order_by(Event.created_at.desc()).limit(5)
        )
        recent_events = recent_events_result.scalars().all()

        techs_result = await self.db.execute(
            select(Project.tech_stack).where(Project.tech_stack.isnot(None))
        )
        all_techs = []
        for row in techs_result.all():
            techs = row[0] if row else None
            if techs:
                all_techs.extend(techs)
        tech_count = {}
        for t in all_techs:
            tech_count[t] = tech_count.get(t, 0) + 1
        top_technologies = sorted(tech_count.items(), key=lambda x: -x[1])[:10]
        top_technologies_list = [
            {"name": name, "count": count}
            for name, count in top_technologies
        ]

        return {
            "total_users": user_stats.get("total_users", 0),
            "active_participants": user_stats.get("active_participants", 0),
            "total_events": events_total.scalar() or 0,
            "total_projects": projects_total.scalar() or 0,
            "total_teams": teams_total.scalar() or 0,
            "universities": user_stats.get("universities", 0),
            "countries": user_stats.get("countries", 0),
            "events_by_status": {
                "published": events_published.scalar() or 0,
                "in_progress": events_in_progress.scalar() or 0,
                "closed": events_closed.scalar() or 0,
            },
            "top_technologies": top_technologies_list,
            "recent_events": [
                {
                    "id": str(e.id),
                    "title": e.title,
                    "status": e.status,
                    "start_date": str(e.start_date),
                    "end_date": str(e.end_date),
                }
                for e in recent_events
            ],
        }

    async def get_event_stats(self, event_id: UUID) -> Dict[str, Any]:
        from app.models.team import Team
        from app.models.evaluation import Evaluation

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
            "total_teams": teams_count.scalar() or 0,
            "total_projects": projects_count.scalar() or 0,
            "submitted_projects": submitted_count.scalar() or 0,
            "total_evaluations": evals_count.scalar() or 0,
        }
