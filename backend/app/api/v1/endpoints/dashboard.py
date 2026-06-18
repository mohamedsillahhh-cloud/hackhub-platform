from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_active_user
from app.models.user import User
from app.services.user_service import UserService
from app.services.export_service import ExportService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def global_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = UserService(db)
    return await service.get_dashboard_stats()


@router.get("/events/{event_id}/stats")
async def event_stats(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = UserService(db)
    return await service.get_event_stats(event_id)


@router.get("/events/{event_id}/export/participants")
async def export_participants(
    event_id: UUID,
    fmt: str = Query("xlsx", regex="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_participants(event_id, current_user, fmt)


@router.get("/events/{event_id}/export/projects")
async def export_projects(
    event_id: UUID,
    fmt: str = Query("xlsx", regex="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_projects(event_id, current_user, fmt)


@router.get("/events/{event_id}/export/ranking")
async def export_ranking(
    event_id: UUID,
    fmt: str = Query("xlsx", regex="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_ranking(event_id, current_user, fmt)


@router.get("/events/{event_id}/export/evaluations")
async def export_evaluations(
    event_id: UUID,
    fmt: str = Query("xlsx", regex="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_evaluations(event_id, current_user, fmt)
