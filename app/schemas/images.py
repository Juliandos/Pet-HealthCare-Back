# ========================================
# app/schemas/images.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional

class ImageUploadResponse(BaseModel):
    """Schema para respuesta de subida de imagen"""
    url: str = Field(..., description="URL pública de la imagen")
    key: str = Field(..., description="Clave del objeto en S3")
    size: int = Field(..., description="Tamaño del archivo en bytes")
    bucket: str = Field(..., description="Nombre del bucket")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://pet-healthcare-images.s3.us-east-1.amazonaws.com/pets/uuid/image.jpg",
                "key": "pets/uuid/image.jpg",
                "size": 245678,
                "bucket": "pet-healthcare-images"
            }
        }

class PetPhotoListResponse(BaseModel):
    """Schema para lista de fotos de mascota"""
    key: str
    size: int
    last_modified: str
    url: str