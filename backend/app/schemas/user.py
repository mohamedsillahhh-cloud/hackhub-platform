from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
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
    new_password: str = Field(..., min_length=6)
