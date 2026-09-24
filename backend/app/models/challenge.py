import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import UUID


class ChallengeCategory(Base):
    __tablename__ = "challenge_categories"
    __table_args__ = (UniqueConstraint("event_id", "name", name="uq_challenge_categories_event_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    challenges = relationship(
        "Challenge",
        back_populates="category",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    criteria = relationship(
        "Criterion",
        back_populates="challenge_category",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class Criterion(Base):
    __tablename__ = "criteria"
    __table_args__ = (
        UniqueConstraint("challenge_category_id", "name", name="uq_criteria_category_name"),
        CheckConstraint("max_score > 0", name="ck_criteria_max_score_positive"),
        CheckConstraint("weight > 0", name="ck_criteria_weight_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("challenge_categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    challenge_category = relationship("ChallengeCategory", back_populates="criteria", lazy="selectin")


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("challenge_categories.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    requirements: Mapped[str] = mapped_column(Text, nullable=True)
    documentation_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="challenges", lazy="selectin")
    category = relationship("ChallengeCategory", back_populates="challenges", lazy="selectin")
