from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class CertificateResponse(BaseModel):
    id: str
    user_id: str
    event_id: str
    type: str
    template_name: Optional[str] = None
    qr_code_url: Optional[str] = None
    verification_code: str
    digital_signature: Optional[str] = None
    issued_at: datetime
    extra_data: Optional[Any] = None

    model_config = {"from_attributes": True}
