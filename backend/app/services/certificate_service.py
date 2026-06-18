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
            extra_data={
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

    async def generate_all_certificates(self, event_id: UUID) -> None:
        from sqlalchemy import select
        from app.models.project import Project, ProjectStatus
        from app.models.team import Team, TeamMember

        event = await self.event_repo.get(event_id)
        if not event:
            return

        projects_result = await self.db.execute(
            select(Project).where(Project.event_id == event_id, Project.status == ProjectStatus.SUBMITTED)
        )
        projects = projects_result.scalars().all()

        user_ids_with_projects = set()
        for project in projects:
            team_result = await self.db.execute(
                select(TeamMember).where(TeamMember.team_id == project.team_id, TeamMember.status == "accepted")
            )
            members = team_result.scalars().all()
            for member in members:
                user_ids_with_projects.add(member.user_id)
                existing = await self.db.execute(
                    select(Certificate).where(
                        Certificate.user_id == member.user_id,
                        Certificate.event_id == event_id,
                        Certificate.type == CertificateType.PARTICIPATION,
                    )
                )
                if not existing.scalar_one_or_none():
                    await self.generate_certificate(member.user_id, event_id, CertificateType.PARTICIPATION)

        from app.services.ranking_service import RankingService
        rsvc = RankingService(self.db)
        entries = await rsvc.get_ranking(event_id)
        top_50_pct = max(1, len(entries) // 2)
        top_3 = entries[:3]

        for entry in entries[:top_50_pct]:
            team_id = entry.get("team_id")
            if not team_id:
                continue
            members = await self.db.execute(
                select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.status == "accepted")
            )
            for member in members.scalars().all():
                existing = await self.db.execute(
                    select(Certificate).where(
                        Certificate.user_id == member.user_id,
                        Certificate.event_id == event_id,
                        Certificate.type == CertificateType.FINALIST,
                    )
                )
                if not existing.scalar_one_or_none():
                    await self.generate_certificate(member.user_id, event_id, CertificateType.FINALIST)

        for entry in top_3:
            team_id = entry.get("team_id")
            if not team_id:
                continue
            members = await self.db.execute(
                select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.status == "accepted")
            )
            for member in members.scalars().all():
                existing = await self.db.execute(
                    select(Certificate).where(
                        Certificate.user_id == member.user_id,
                        Certificate.event_id == event_id,
                        Certificate.type == CertificateType.WINNER,
                    )
                )
                if not existing.scalar_one_or_none():
                    await self.generate_certificate(member.user_id, event_id, CertificateType.WINNER)

        await self.generate_certificate(event.organizer_id, event_id, CertificateType.ORGANIZER)
