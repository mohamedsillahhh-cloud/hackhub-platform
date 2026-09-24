from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    UserCreate,
    UserLogin,
    UserPrivateResponse,
    UserStatsResponse,
    UserUpdate,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def set_token_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )


def clear_token_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.AUTH_RATE_LIMIT_REGISTER)
async def register(
    request: Request,
    user_data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.register(user_data)
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
    }


@router.post("/login")
@limiter.limit(settings.AUTH_RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.login(credentials.email, credentials.password)
    await db.commit()
    set_token_cookies(response, result["access_token"], result["refresh_token"])
    return {"message": "Login successful"}


@router.post("/refresh")
@limiter.limit(settings.AUTH_RATE_LIMIT_REFRESH)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    service = AuthService(db)
    result = await service.refresh_token(refresh_token_str)
    await db.commit()
    set_token_cookies(response, result["access_token"], result["refresh_token"])
    return {"message": "Token refreshed"}


@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(request.cookies.get("refresh_token") or request.cookies.get("access_token"))
    clear_token_cookies(response)
    return {"message": "Logged out successfully"}


@router.post("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.verify_email(token)
    return {"message": "Email verified successfully"}


@router.post("/password-reset")
@limiter.limit(settings.AUTH_RATE_LIMIT_RESET)
async def password_reset(request: Request, payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.send_password_reset(payload.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
@limiter.limit(settings.AUTH_RATE_LIMIT_RESET)
async def password_reset_confirm(request: Request, payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.confirm_password_reset(payload.token, payload.new_password)
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserPrivateResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserPrivateResponse)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update_profile(current_user.id, profile_data)


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_profile_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).get_user_stats(current_user.id)
