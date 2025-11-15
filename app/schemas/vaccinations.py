# ========================================
# app/schemas/vaccinations.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class VaccinationBase(BaseModel):
    vaccine_name: str = Field(..., min_length=1, max_length=200)
    manufacturer: Optional[str] = Field(None, max_length=200)
    lot_number: Optional[str] = Field(None, max_length=100)
    date_administered: date
    next_due: Optional[date] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    proof_document_id: Optional[str] = None

class VaccinationCreate(VaccinationBase):
    pet_id: str

class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = Field(None, min_length=1, max_length=200)
    manufacturer: Optional[str] = Field(None, max_length=200)
    lot_number: Optional[str] = Field(None, max_length=100)
    date_administered: Optional[date] = None
    next_due: Optional[date] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    proof_document_id: Optional[str] = None

class VaccinationResponse(VaccinationBase):
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

