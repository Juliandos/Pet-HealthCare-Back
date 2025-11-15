# ========================================
# app/schemas/reminders.py
# ========================================
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
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
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ReminderFrequency: lambda v: v.value
        }


