import uuid
import hashlib
import qrcode
import io
import base64
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate, CertificateType
from app.repositories.base import BaseRepository
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.utils.helpers import generate_unique_code


class CertificateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cert_repo = BaseRepository(Certificate, db)
        self.event_repo = EventRepository(db)
        self.user_repo = UserRepository(db)

    async def generate_certificate(
        self,
        user_id: UUID,
        event_id: UUID,
        cert_type: CertificateType,
        template_name: Optional[str] = None,
    ) -> Certificate:
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        verification_code = generate_unique_code(16)
        while True:
            existing = await self.cert_repo.get(
                UUID(hashlib.md5(verification_code.encode()).hexdigest()[:32])
            )
            if not existing:
                break
            verification_code = generate_unique_code(16)

        signature_data = f"{user_id}-{event_id}-{cert_type.value}-{verification_code}"
        digital_signature = hashlib.sha256(signature_data.encode()).hexdigest()

        qr_data = f"https://hackhub.app/certificates/verify/{verification_code}"
        qr_img = qrcode.make(qr_data)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_base64}"

        certificate = await self.cert_repo.create(
            user_id=user_id,
            event_id=event_id,
            type=cert_type,
            template_name=template_name,
            qr_code_url=qr_code_url,
            verification_code=verification_code,
            digital_signature=digital_signature,
            metadata={
                "user_name": user.full_name or user.username,
                "event_title": event.title,
                "event_date": event.start_date.isoformat() if event.start_date else None,
            },
        )

        return certificate

    async def verify_certificate(self, verification_code: str) -> Certificate:
        from sqlalchemy import select
        result = await self.db.execute(
            select(Certificate).where(Certificate.verification_code == verification_code)
        )
        certificate = result.scalar_one_or_none()
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found or invalid verification code",
            )
        return certificate

    async def get_certificate(self, certificate_id: UUID) -> Certificate:
        certificate = await self.cert_repo.get(certificate_id)
        if not certificate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
        return certificate

    async def get_user_certificates(self, user_id: UUID) -> list:
        from sqlalchemy import select
        result = await self.db.execute(
            select(Certificate).where(Certificate.user_id == user_id).order_by(Certificate.issued_at.desc())
        )
        return list(result.scalars().all())
