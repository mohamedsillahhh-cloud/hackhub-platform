from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
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
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def set_token_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
        path="/api/v1/auth/refresh",
    )


def clear_token_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(user_data)
    return {"id": str(user.id), "email": user.email, "username": user.username, "full_name": user.full_name}


@router.post("/login")
async def login(credentials: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login(credentials.email, credentials.password)
    set_token_cookies(response, result["access_token"], result["refresh_token"])
    return {"message": "Login successful"}


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    service = AuthService(db)
    result = await service.refresh_token(refresh_token_str)
    set_token_cookies(response, result["access_token"], result["refresh_token"])
    return {"message": "Token refreshed"}


@router.post("/logout")
async def logout(response: Response):
    clear_token_cookies(response)
    return {"message": "Logged out successfully"}


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
