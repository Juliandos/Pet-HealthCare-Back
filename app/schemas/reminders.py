# ========================================
# app/schemas/reminders.py
# ========================================
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models import ReminderFrequency

class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_time: datetime
    timezone: Optional[str] = "UTC"
    frequency: ReminderFrequency = ReminderFrequency.once
    rrule: Optional[str] = None
    is_active: bool = True
    notify_by_email: bool = True
    notify_in_app: bool = True
    pet_id: Optional[str] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_time: Optional[datetime] = None
    timezone: Optional[str] = None
    frequency: Optional[ReminderFrequency] = None
    rrule: Optional[str] = None
    is_active: Optional[bool] = None
    notify_by_email: Optional[bool] = None
    notify_in_app: Optional[bool] = None
    pet_id: Optional[str] = None

class ReminderResponse(ReminderBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    @root_validator(pre=True)
    def convert_uuids_to_strings(cls, values):
        """Convierte todos los UUIDs a strings antes de la validación"""
        if isinstance(values, dict):
            for key in ['id', 'owner_id', 'pet_id']:
                if key in values and values[key] is not None:
                    if isinstance(values[key], UUID):
                        values[key] = str(values[key])
        elif hasattr(values, '__dict__'):
            # Si es un objeto SQLAlchemy, convertir sus atributos
            for attr in ['id', 'owner_id', 'pet_id']:
                if hasattr(values, attr):
                    value = getattr(values, attr)
                    if isinstance(value, UUID):
                        setattr(values, attr, str(value))
        return values
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ReminderFrequency: lambda v: v.value,
            UUID: lambda v: str(v) if v else None
        }


