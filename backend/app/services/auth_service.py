from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_action_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    token_hash_matches,
    verify_password,
)
from app.models.auth_session import AuthSession
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


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

        verification_token = create_action_token(
            data={"sub": str(user.id)},
            action="verify_email",
            expires_delta=timedelta(days=1),
        )

        from app.utils.email import send_email

        verification_url = f"{settings.APP_URL.rstrip('/')}/auth/verify-email?token={verification_token}"
        await send_email(
            to=user.email,
            subject="Verify your HackHub account",
            body_html=f"<p>Click <a href='{verification_url}'>here</a> to verify your email.</p>",
        )

        return user

    async def login(self, email: str, password: str) -> dict:
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

        session = AuthSession(
            user_id=user.id,
            refresh_token_hash="pending",
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(session)
        await self.db.flush()

        token_data = {"sub": str(user.id), "sid": str(session.id)}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        session.refresh_token_hash = hash_token(refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh_token(self, refresh_token_str: str) -> dict:
        payload = decode_token(refresh_token_str)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        try:
            user_id = UUID(payload["sub"])
            session_id = UUID(payload["sid"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )

        result = await self.db.execute(
            select(AuthSession).where(
                AuthSession.id == session_id,
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
        )
        session = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if session is None or self._as_utc(session.expires_at) <= now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or revoked",
            )
        if not token_hash_matches(refresh_token_str, session.refresh_token_hash):
            session.revoked_at = now
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token reuse detected",
            )

        user = await self.user_repo.get(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        token_data = {"sub": str(user.id), "sid": str(session.id)}
        access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)
        session.refresh_token_hash = hash_token(new_refresh_token)
        session.last_used_at = now

        return {"access_token": access_token, "refresh_token": new_refresh_token}

    async def logout(self, token: str | None) -> None:
        if not token:
            return
        payload = decode_token(token)
        if payload is None:
            return
        try:
            session_id = UUID(payload["sid"])
        except (KeyError, TypeError, ValueError):
            return
        await self.db.execute(
            update(AuthSession)
            .where(AuthSession.id == session_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    async def verify_email(self, token: str) -> None:
        payload = decode_token(token)
        if payload is None or payload.get("type") != "action" or payload.get("action") != "verify_email":
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

        reset_token = create_action_token(
            data={"sub": str(user.id), "version": user.password_reset_version},
            action="password_reset",
            expires_delta=timedelta(minutes=30),
        )

        from app.utils.email import send_email

        reset_url = f"{settings.APP_URL.rstrip('/')}/auth/reset-password?token={reset_token}"
        await send_email(
            to=user.email,
            subject="Reset your HackHub password",
            body_html=f"<p>Click <a href='{reset_url}'>here</a> to reset your password.</p>",
        )

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        payload = decode_token(token)
        if payload is None or payload.get("type") != "action" or payload.get("action") != "password_reset":
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
        if payload.get("version") != user.password_reset_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        await self.user_repo.update(
            user.id,
            hashed_password=get_password_hash(new_password),
            password_reset_version=user.password_reset_version + 1,
        )
        await self.db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
