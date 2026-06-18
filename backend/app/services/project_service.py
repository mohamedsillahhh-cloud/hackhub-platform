from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.event_repository import EventRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.event_repo = EventRepository(db)
        self.team_repo = TeamRepository(db)

    async def create_project(self, event_id: UUID, project_data: ProjectCreate, user_id: UUID) -> Project:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        teams = await self.team_repo.get_user_teams(user_id)
        user_team = None
        for team in teams:
            if str(team.event_id) == str(event_id):
                user_team = team
                break
        if not user_team:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be part of a team in this event to create a project",
            )

        is_leader = any(
            str(m.user_id) == str(user_id) and m.role == "leader"
            for m in user_team.members
        )
        if not is_leader:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the team leader can create a project",
            )

        existing = await self.project_repo.get_by_team(user_team.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your team already has a project",
            )

        project = await self.project_repo.create(
            team_id=user_team.id,
            event_id=event_id,
            challenge_id=project_data.challenge_id,
            name=project_data.name,
            description=project_data.description,
            github_url=project_data.github_url,
            demo_video_url=project_data.demo_video_url,
            presentation_url=project_data.presentation_url,
            tech_stack=project_data.tech_stack or [],
        )
        return project

    async def update_project(self, project_id: UUID, project_data: ProjectUpdate, user_id: UUID) -> Project:
        project = await self.project_repo.get(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        team = await self.team_repo.get_team_with_members(project.team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        is_leader = str(team.leader_id) == str(user_id)
        if not is_leader:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the team leader can update the project",
            )

        if project.status == ProjectStatus.FINALIZED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a finalized project",
            )

        update_data = project_data.model_dump(exclude_unset=True)
        updated = await self.project_repo.update(project_id, **update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return updated

    async def submit_project(self, project_id: UUID, user_id: UUID) -> Project:
        project = await self.project_repo.get(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        team = await self.team_repo.get_team_with_members(project.team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        is_leader = str(team.leader_id) == str(user_id)
        if not is_leader:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the team leader can submit the project",
            )

        if project.status == ProjectStatus.FINALIZED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project already finalized",
            )

        updated = await self.project_repo.update(
            project_id,
            status=ProjectStatus.SUBMITTED,
            submitted_at=datetime.utcnow(),
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return updated

    async def list_event_projects(self, event_id: UUID) -> List[Project]:
        return await self.project_repo.get_by_event(event_id)

    async def get_team_project(self, team_id: UUID) -> Optional[Project]:
        return await self.project_repo.get_by_team(team_id)

    async def get_project(self, project_id: UUID) -> Project:
        project = await self.project_repo.get(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project
