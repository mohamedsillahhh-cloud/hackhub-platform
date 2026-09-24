from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class CertificateResponse(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID
    type: str
    template_name: Optional[str] = None
    qr_code_url: Optional[str] = None
    verification_code: str
    digital_signature: Optional[str] = None
    issued_at: datetime
    extra_data: Optional[Any] = None

    model_config = {"from_attributes": True}
