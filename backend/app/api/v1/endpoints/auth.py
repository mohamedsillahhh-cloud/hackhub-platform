from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(credentials.email, credentials.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_token(request.refresh_token)


@router.post("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.verify_email(token)
    return {"message": "Email verified successfully"}


@router.post("/password-reset")
async def password_reset(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.send_password_reset(request.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def password_reset_confirm(request: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.confirm_password_reset(request.token, request.new_password)
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update_profile(current_user.id, profile_data)
