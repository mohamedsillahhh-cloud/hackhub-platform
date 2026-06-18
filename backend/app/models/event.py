import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Text, Integer, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str] = mapped_column(String(500), nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    regulations: Mapped[str] = mapped_column(Text, nullable=True)
    schedule: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    sponsors: Mapped[dict] = mapped_column(JSON, nullable=True, default=list)
    prizes: Mapped[dict] = mapped_column(JSON, nullable=True, default=list)
    faq: Mapped[dict] = mapped_column(JSON, nullable=True, default=list)
    max_team_size: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    min_team_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    organizer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organizer = relationship("User", lazy="selectin")
    organization = relationship("Organization", back_populates="events", lazy="selectin")
    challenges = relationship("Challenge", back_populates="event", lazy="selectin", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="event", lazy="selectin", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="event", lazy="selectin", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="event", lazy="selectin", cascade="all, delete-orphan")
