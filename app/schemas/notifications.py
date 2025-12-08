# ========================================
# app/schemas/notifications.py
# ========================================
from pydantic import BaseModel, root_validator
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

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
    
    @root_validator(pre=True)
    def convert_uuids_to_strings(cls, values):
        """Convierte todos los UUIDs a strings antes de la validación"""
        if isinstance(values, dict):
            for key in ['id', 'owner_id', 'reminder_id', 'pet_id']:
                if key in values and values[key] is not None:
                    if isinstance(values[key], UUID):
                        values[key] = str(values[key])
        elif hasattr(values, '__dict__'):
            # Si es un objeto SQLAlchemy, convertir sus atributos
            for attr in ['id', 'owner_id', 'reminder_id', 'pet_id']:
                if hasattr(values, attr):
                    value = getattr(values, attr)
                    if isinstance(value, UUID):
                        setattr(values, attr, str(value))
        return values
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v) if v else None
        }


