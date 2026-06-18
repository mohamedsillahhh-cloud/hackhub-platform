import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class CertificateType(str, enum.Enum):
    PARTICIPATION = "participation"
    FINALIST = "finalist"
    WINNER = "winner"
    JUDGE = "judge"
    ORGANIZER = "organizer"


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    type: Mapped[CertificateType] = mapped_column(Enum(CertificateType), nullable=False)
    template_name: Mapped[str] = mapped_column(String(255), nullable=True)
    qr_code_url: Mapped[str] = mapped_column(String(500), nullable=True)
    verification_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    digital_signature: Mapped[str] = mapped_column(Text, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)

    user = relationship("User", back_populates="certificates", lazy="selectin")
    event = relationship("Event", back_populates="certificates", lazy="selectin")
