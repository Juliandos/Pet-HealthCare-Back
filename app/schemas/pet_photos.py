# ========================================
# app/schemas/pet_photos.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PetPhotoBase(BaseModel):
    file_name: Optional[str] = Field(None, max_length=500)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = None

class PetPhotoCreate(PetPhotoBase):
    pet_id: str
    data: Optional[bytes] = None  # Para subir archivo directamente

class PetPhotoUpdate(BaseModel):
    file_name: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = None

class PetPhotoResponse(PetPhotoBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }