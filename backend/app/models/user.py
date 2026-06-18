import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Text, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    JUDGE = "judge"
    PARTICIPANT = "participant"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.PARTICIPANT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    university: Mapped[str] = mapped_column(String(255), nullable=True)
    course: Mapped[str] = mapped_column(String(255), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    skills: Mapped[list] = mapped_column(ARRAY(String), nullable=True, default=list)
    github_url: Mapped[str] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str] = mapped_column(String(500), nullable=True)
    experience_level: Mapped[str] = mapped_column(String(50), nullable=True)
    preferred_languages: Mapped[list] = mapped_column(ARRAY(String), nullable=True, default=list)
    preferred_frameworks: Mapped[list] = mapped_column(ARRAY(String), nullable=True, default=list)
    interest_areas: Mapped[list] = mapped_column(ARRAY(String), nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    teams = relationship("TeamMember", back_populates="user", lazy="selectin")
    evaluations = relationship("Evaluation", back_populates="judge", lazy="selectin")
    notifications = relationship("Notification", back_populates="user", lazy="selectin")
    certificates = relationship("Certificate", back_populates="user", lazy="selectin")
    organizations = relationship("Organization", back_populates="owner", lazy="selectin")
