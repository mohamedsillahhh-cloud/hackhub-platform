from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organizer
from app.models.user import User
from app.schemas.certificate import CertificateResponse
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/verify/{code}", response_model=CertificateResponse)
async def verify_certificate(code: str, db: AsyncSession = Depends(get_db)):
    service = CertificateService(db)
    certificate = await service.verify_certificate(code)
    return certificate


@router.get("/my")
async def get_my_certificates(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = CertificateService(db)
    return await service.get_user_certificates(current_user.id)


@router.post("/events/{event_id}/generate")
async def generate_event_certificates(
    event_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_organizer),
    db: AsyncSession = Depends(get_db),
):
    service = CertificateService(db)
    background_tasks.add_task(service.generate_all_certificates, event_id)
    return {"message": "Certificate generation started", "event_id": str(event_id)}


@router.get("/download/{certificate_id}")
async def download_certificate_html(
    certificate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = CertificateService(db)
    certificate = await service.get_certificate(certificate_id)
    extra = certificate.extra_data or {}
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Certificate - {certificate.verification_code}</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <div style="border: 3px solid #333; padding: 40px; max-width: 700px; margin: auto;">
            <h1>Certificate of {certificate.type.value.title()}</h1>
            <p>This certificate is awarded to</p>
            <h2>{extra.get('user_name', 'Participant')}</h2>
            <p>for the event</p>
            <h3>{extra.get('event_title', 'Hackathon')}</h3>
            <p>Issued on: {certificate.issued_at.strftime('%B %d, %Y')}</p>
            <p>Verification Code: <strong>{certificate.verification_code}</strong></p>
            <img src="{certificate.qr_code_url}" alt="QR Code" style="width: 150px; height: 150px;"/>
            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                Verify at: /certificates/verify/{certificate.verification_code}
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
