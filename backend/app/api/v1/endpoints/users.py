from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_admin
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.schemas.certificate import CertificateResponse
from app.services.user_service import UserService
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    skills: Optional[str] = None,
    university: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = UserService(db)
    skill_list = skills.split(",") if skills else None
    items, total = await service.list_users(
        page=page,
        size=size,
        role=role,
        skills=skill_list,
        university=university,
        country=country,
        search=search,
    )
    return items


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = UserService(db)
    return await service.get_user_by_id(user_id)


@router.get("/{user_id}/certificates", response_model=List[CertificateResponse])
async def get_user_certificates(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = CertificateService(db)
    return await service.get_user_certificates(user_id)
