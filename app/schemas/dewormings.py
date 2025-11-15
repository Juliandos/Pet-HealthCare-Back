# ========================================
# app/schemas/dewormings.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class DewormingBase(BaseModel):
    medication: Optional[str] = Field(None, max_length=200)
    date_administered: date
    next_due: Optional[date] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

class DewormingCreate(DewormingBase):
    pet_id: str

class DewormingUpdate(BaseModel):
    medication: Optional[str] = Field(None, max_length=200)
    date_administered: Optional[date] = None
    next_due: Optional[date] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

class DewormingResponse(DewormingBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None
        }