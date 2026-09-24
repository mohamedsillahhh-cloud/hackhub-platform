from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate
from app.models.event import Event, EventStatus
from app.models.project import Project
from app.models.team import InviteStatus, Team, TeamMember
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
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_profile(self, user_id: UUID, profile_data: UserUpdate) -> User:
        update_data = profile_data.model_dump(exclude_unset=True)
        user = await self.user_repo.update(user_id, **update_data)
        if not user:
            from fastapi import HTTPException

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

    async def get_dashboard_stats(self, organizer_id: Optional[UUID] = None) -> Dict[str, Any]:
        event_scope = Event.organizer_id == organizer_id if organizer_id else None

        events_total_query = select(func.count(Event.id))
        events_published_query = select(func.count(Event.id)).where(Event.status == EventStatus.PUBLISHED)
        events_in_progress_query = select(func.count(Event.id)).where(Event.status == EventStatus.IN_PROGRESS)
        events_closed_query = select(func.count(Event.id)).where(Event.status == EventStatus.CLOSED)
        projects_total_query = select(func.count(Project.id))
        teams_total_query = select(func.count(Team.id))
        recent_events_query = select(Event)
        techs_query = select(Project.tech_stack).where(Project.tech_stack.isnot(None))

        if event_scope is not None:
            events_total_query = events_total_query.where(event_scope)
            events_published_query = events_published_query.where(event_scope)
            events_in_progress_query = events_in_progress_query.where(event_scope)
            events_closed_query = events_closed_query.where(event_scope)
            projects_total_query = projects_total_query.join(Event, Project.event_id == Event.id).where(event_scope)
            teams_total_query = teams_total_query.join(Event, Team.event_id == Event.id).where(event_scope)
            techs_query = techs_query.join(Event, Project.event_id == Event.id).where(event_scope)
            recent_events_query = recent_events_query.where(event_scope)

            participant_scope = (
                select(func.count(func.distinct(TeamMember.user_id)))
                .join(Team, TeamMember.team_id == Team.id)
                .join(Event, Team.event_id == Event.id)
                .where(TeamMember.status == InviteStatus.ACCEPTED, event_scope)
            )
            participant_count = await self.db.scalar(participant_scope) or 0
            universities = (
                await self.db.scalar(
                    select(func.count(func.distinct(User.university)))
                    .join(TeamMember, TeamMember.user_id == User.id)
                    .join(Team, TeamMember.team_id == Team.id)
                    .join(Event, Team.event_id == Event.id)
                    .where(
                        TeamMember.status == InviteStatus.ACCEPTED,
                        User.university.isnot(None),
                        event_scope,
                    )
                )
                or 0
            )
            countries = (
                await self.db.scalar(
                    select(func.count(func.distinct(User.country)))
                    .join(TeamMember, TeamMember.user_id == User.id)
                    .join(Team, TeamMember.team_id == Team.id)
                    .join(Event, Team.event_id == Event.id)
                    .where(
                        TeamMember.status == InviteStatus.ACCEPTED,
                        User.country.isnot(None),
                        event_scope,
                    )
                )
                or 0
            )
            user_stats = {
                "total_users": participant_count,
                "active_participants": participant_count,
                "universities": universities,
                "countries": countries,
            }
        else:
            user_stats = await self.user_repo.get_dashboard_stats()

        events_total = await self.db.execute(events_total_query)
        events_published = await self.db.execute(events_published_query)
        events_in_progress = await self.db.execute(events_in_progress_query)
        events_closed = await self.db.execute(events_closed_query)
        projects_total = await self.db.execute(projects_total_query)
        teams_total = await self.db.execute(teams_total_query)

        recent_events_result = await self.db.execute(recent_events_query.order_by(Event.created_at.desc()).limit(5))
        recent_events = recent_events_result.scalars().all()

        techs_result = await self.db.execute(techs_query)
        all_techs = []
        for row in techs_result.all():
            techs = row[0] if row else None
            if techs:
                all_techs.extend(techs)
        tech_count = {}
        for t in all_techs:
            tech_count[t] = tech_count.get(t, 0) + 1
        top_technologies = sorted(tech_count.items(), key=lambda x: -x[1])[:10]
        top_technologies_list = [{"name": name, "count": count} for name, count in top_technologies]

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

    async def get_public_dashboard_stats(self) -> Dict[str, int]:
        visible_events = Event.status.in_([EventStatus.PUBLISHED, EventStatus.IN_PROGRESS, EventStatus.CLOSED])
        event_ids = select(Event.id).where(visible_events)

        total_events = await self.db.scalar(select(func.count(Event.id)).where(visible_events))
        total_projects = await self.db.scalar(select(func.count(Project.id)).where(Project.event_id.in_(event_ids)))
        total_teams = await self.db.scalar(select(func.count(Team.id)).where(Team.event_id.in_(event_ids)))
        active_participants = await self.db.scalar(
            select(func.count(func.distinct(TeamMember.user_id)))
            .join(Team, TeamMember.team_id == Team.id)
            .where(
                Team.event_id.in_(event_ids),
                TeamMember.status == InviteStatus.ACCEPTED,
            )
        )
        return {
            "total_events": total_events or 0,
            "total_projects": total_projects or 0,
            "total_teams": total_teams or 0,
            "active_participants": active_participants or 0,
        }

    async def get_user_stats(self, user_id: UUID) -> Dict[str, int]:
        events = await self.db.scalar(
            select(func.count(func.distinct(Team.event_id)))
            .join(TeamMember, TeamMember.team_id == Team.id)
            .where(
                TeamMember.user_id == user_id,
                TeamMember.status == InviteStatus.ACCEPTED,
            )
        )
        projects = await self.db.scalar(
            select(func.count(Project.id))
            .join(TeamMember, TeamMember.team_id == Project.team_id)
            .where(
                TeamMember.user_id == user_id,
                TeamMember.status == InviteStatus.ACCEPTED,
            )
        )
        certificates = await self.db.scalar(select(func.count(Certificate.id)).where(Certificate.user_id == user_id))
        return {
            "events": events or 0,
            "projects": projects or 0,
            "certificates": certificates or 0,
        }

    async def get_event_stats(self, event_id: UUID) -> Dict[str, Any]:
        from app.models.evaluation import Evaluation

        teams_count = await self.db.execute(select(func.count(Team.id)).where(Team.event_id == event_id))
        projects_count = await self.db.execute(select(func.count(Project.id)).where(Project.event_id == event_id))
        participants_count = await self.db.execute(
            select(func.count(func.distinct(TeamMember.user_id)))
            .join(Team, TeamMember.team_id == Team.id)
            .where(Team.event_id == event_id, TeamMember.status == InviteStatus.ACCEPTED)
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
            "total_participants": participants_count.scalar() or 0,
            "submitted_projects": submitted_count.scalar() or 0,
            "total_evaluations": evals_count.scalar() or 0,
        }
