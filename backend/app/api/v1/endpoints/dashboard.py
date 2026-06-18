from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_active_user
from app.models.user import User
from app.services.user_service import UserService

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
