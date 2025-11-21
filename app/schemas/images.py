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
    photo_id: Optional[str] = Field(None, description="ID del registro en pet_photos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://pet-healthcare-images.s3.us-east-1.amazonaws.com/pets/uuid/image.jpg",
                "key": "pets/uuid/image.jpg",
                "size": 245678,
                "bucket": "pet-healthcare-images",
                "photo_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class PetPhotoListResponse(BaseModel):
    """Schema para lista de fotos de mascota"""
    id: str = Field(..., description="ID del registro en pet_photos")
    pet_id: str = Field(..., description="ID de la mascota")
    file_name: Optional[str] = Field(None, description="Nombre del archivo")
    file_size_bytes: Optional[int] = Field(None, description="Tamaño en bytes")
    mime_type: Optional[str] = Field(None, description="Tipo MIME")
    url: str = Field(..., description="URL pública de la imagen")
    key: str = Field(..., description="Clave del objeto en S3 (para compatibilidad)")
    size: int = Field(..., description="Tamaño del archivo en bytes")
    last_modified: str = Field(..., description="Fecha de última modificación")
    created_at: Optional[str] = Field(None, description="Fecha de creación")
    is_profile: bool = Field(False, description="True si es foto de perfil, False si es de galería")