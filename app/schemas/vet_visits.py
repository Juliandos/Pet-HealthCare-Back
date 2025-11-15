# ========================================
# app/schemas/vet_visits.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VetVisitBase(BaseModel):
    visit_date: datetime
    reason: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    documents_id: Optional[str] = None

class VetVisitCreate(VetVisitBase):
    pet_id: str

class VetVisitUpdate(BaseModel):
    visit_date: Optional[datetime] = None
    reason: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    documents_id: Optional[str] = None

class VetVisitResponse(VetVisitBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }