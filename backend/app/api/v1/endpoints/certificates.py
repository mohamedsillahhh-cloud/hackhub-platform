import base64
import io
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_organizer,
    require_event_manager,
)
from app.models.user import User, UserRole
from app.schemas.certificate import CertificateResponse
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/verify/{code}", response_model=CertificateResponse)
async def verify_certificate(code: str, db: AsyncSession = Depends(get_db)):
    service = CertificateService(db)
    certificate = await service.verify_certificate(code)
    return certificate


@router.get("/my", response_model=List[CertificateResponse])
async def get_my_certificates(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = CertificateService(db)
    return await service.get_user_certificates(current_user.id)


@router.post("/events/{event_id}/generate")
async def generate_event_certificates(
    event_id: UUID,
    current_user: User = Depends(get_current_organizer),
    db: AsyncSession = Depends(get_db),
):
    await require_event_manager(db, event_id, current_user)
    service = CertificateService(db)
    await service.generate_all_certificates(event_id)
    return {"message": "Certificates generated", "event_id": str(event_id)}


@router.get("/download/{certificate_id}")
async def download_certificate_pdf(
    certificate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = CertificateService(db)
    certificate = await service.get_certificate(certificate_id)
    if current_user.role != UserRole.ADMIN and certificate.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    extra = certificate.extra_data or {}
    user_name = str(extra.get("user_name", "Participant"))
    event_title = str(extra.get("event_title", "Hackathon"))
    verification_code = certificate.verification_code
    buffer = io.BytesIO()
    page_width, page_height = landscape(A4)
    pdf_canvas = canvas.Canvas(buffer, pagesize=(page_width, page_height), pageCompression=1)
    pdf_canvas.setTitle(f"HackHub Certificate - {verification_code}")
    pdf_canvas.setLineWidth(3)
    pdf_canvas.rect(28, 28, page_width - 56, page_height - 56)
    pdf_canvas.setFont("Helvetica-Bold", 28)
    pdf_canvas.drawCentredString(
        page_width / 2,
        page_height - 105,
        f"Certificate of {certificate.type.value.title()}",
    )
    pdf_canvas.setFont("Helvetica", 13)
    pdf_canvas.drawCentredString(page_width / 2, page_height - 155, "This certificate is awarded to")
    pdf_canvas.setFont("Helvetica-Bold", 24)
    pdf_canvas.drawCentredString(page_width / 2, page_height - 195, user_name[:70])
    pdf_canvas.setFont("Helvetica", 13)
    pdf_canvas.drawCentredString(page_width / 2, page_height - 235, "for the event")
    pdf_canvas.setFont("Helvetica-Bold", 19)
    pdf_canvas.drawCentredString(page_width / 2, page_height - 270, event_title[:85])
    pdf_canvas.setFont("Helvetica", 11)
    pdf_canvas.drawCentredString(
        page_width / 2,
        105,
        f"Issued on {certificate.issued_at.strftime('%B %d, %Y')} | Verification: {verification_code}",
    )
    if certificate.qr_code_url and "," in certificate.qr_code_url:
        qr_bytes = base64.b64decode(certificate.qr_code_url.split(",", 1)[1])
        pdf_canvas.drawImage(ImageReader(io.BytesIO(qr_bytes)), page_width - 145, 48, width=82, height=82)
    pdf_canvas.save()
    pdf = buffer.getvalue()
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="hackhub-{verification_code}.pdf"'},
    )
