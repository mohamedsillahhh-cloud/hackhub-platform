from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    category: str
    title: str
    message: str
    data: Optional[Any] = None
    read: bool
    sent_at: datetime
    read_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
