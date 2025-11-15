# ========================================
# app/schemas/notifications.py
# ========================================
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class NotificationBase(BaseModel):
    reminder_id: Optional[str] = None
    pet_id: Optional[str] = None
    sent_at: datetime
    method: Optional[str] = None
    status: Optional[str] = None
    provider_response: Optional[Any] = None

class NotificationCreate(NotificationBase):
    owner_id: str

class NotificationUpdate(BaseModel):
    method: Optional[str] = None
    status: Optional[str] = None
    provider_response: Optional[Any] = None

class NotificationResponse(NotificationBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


