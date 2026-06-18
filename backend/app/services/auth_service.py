from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserUpdate


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> User:
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        user = await self.user_repo.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.PARTICIPANT,
        )

        verification_token = create_access_token(
            data={"sub": str(user.id), "action": "verify_email"},
            expires_delta=None,
        )

        from app.utils.email import send_email
        verification_url = f"http://localhost:3000/verify-email?token={verification_token}"
        await send_email(
            to=user.email,
            subject="Verify your HackHub account",
            body_html=f"<p>Click <a href='{verification_url}'>here</a> to verify your email.</p>",
        )

        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        user = await self.user_repo.get(UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def verify_email(self, token: str) -> None:
        payload = decode_token(token)
        if payload is None or payload.get("action") != "verify_email":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        user_id = payload.get("sub")
        user = await self.user_repo.get(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await self.user_repo.update(user.id, is_verified=True)

    async def send_password_reset(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return

        reset_token = create_access_token(
            data={"sub": str(user.id), "action": "password_reset"},
            expires_delta=None,
        )

        from app.utils.email import send_email
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        await send_email(
            to=user.email,
            subject="Reset your HackHub password",
            body_html=f"<p>Click <a href='{reset_url}'>here</a> to reset your password.</p>",
        )

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        payload = decode_token(token)
        if payload is None or payload.get("action") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user_id = payload.get("sub")
        user = await self.user_repo.get(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await self.user_repo.update(user.id, hashed_password=get_password_hash(new_password))
