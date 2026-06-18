from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.project import Project, ProjectTechnology
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/events/{event_id}/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(event_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_event_projects(event_id)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    event_id: UUID,
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = ProjectService(db)
    return await service.create_project(event_id, project_data, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(event_id: UUID, project_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.get_project(project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    event_id: UUID,
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = ProjectService(db)
    return await service.update_project(project_id, project_data, current_user.id)


@router.post("/{project_id}/submit", response_model=ProjectResponse)
async def submit_project(
    event_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = ProjectService(db)
    return await service.submit_project(project_id, current_user.id)
