from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=256)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=256)


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    university: Optional[str] = None
    course: Optional[str] = None
    country: Optional[str] = None
    skills: Optional[List[str]] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_languages: Optional[List[str]] = None
    preferred_frameworks: Optional[List[str]] = None
    interest_areas: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    size: int


class UserPrivateResponse(UserResponse):
    telegram_chat_id: Optional[str] = None


class UserStatsResponse(BaseModel):
    events: int
    projects: int
    certificates: int


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    university: Optional[str] = None
    course: Optional[str] = None
    country: Optional[str] = None
    skills: Optional[List[str]] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_languages: Optional[List[str]] = None
    preferred_frameworks: Optional[List[str]] = None
    interest_areas: Optional[List[str]] = None
    telegram_chat_id: Optional[str] = Field(None, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=256)
