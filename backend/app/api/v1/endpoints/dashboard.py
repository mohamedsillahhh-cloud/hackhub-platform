from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_organizer,
    require_event_manager,
)
from app.models.user import User, UserRole
from app.schemas.dashboard import PublicDashboardStats
from app.services.export_service import ExportService
from app.services.user_service import UserService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/public-stats", response_model=PublicDashboardStats)
async def public_stats(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_public_dashboard_stats()


@router.get("/stats")
async def global_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    service = UserService(db)
    organizer_id = None if current_user.role == UserRole.ADMIN else current_user.id
    return await service.get_dashboard_stats(organizer_id=organizer_id)


@router.get("/events/{event_id}/stats")
async def event_stats(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await require_event_manager(db, event_id, current_user)
    service = UserService(db)
    return await service.get_event_stats(event_id)


@router.get("/events/{event_id}/export/participants")
async def export_participants(
    event_id: UUID,
    fmt: str = Query("xlsx", pattern="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_participants(event_id, current_user, fmt)


@router.get("/events/{event_id}/export/projects")
async def export_projects(
    event_id: UUID,
    fmt: str = Query("xlsx", pattern="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_projects(event_id, current_user, fmt)


@router.get("/events/{event_id}/export/ranking")
async def export_ranking(
    event_id: UUID,
    fmt: str = Query("xlsx", pattern="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_ranking(event_id, current_user, fmt)


@router.get("/events/{event_id}/export/evaluations")
async def export_evaluations(
    event_id: UUID,
    fmt: str = Query("xlsx", pattern="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    svc = ExportService(db)
    return await svc.export_evaluations(event_id, current_user, fmt)
