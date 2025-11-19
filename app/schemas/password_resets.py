# ========================================
# app/schemas/password_resets.py
# ========================================
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PasswordResetBase(BaseModel):
    """Schema base para password reset"""
    token: str = Field(..., min_length=32, description="Token de reseteo")
    expires_at: datetime = Field(..., description="Fecha de expiración del token")
    used: bool = Field(default=False, description="Si el token ya fue usado")

class PasswordResetCreate(PasswordResetBase):
    """Schema para crear un password reset (interno)"""
    user_id: str = Field(..., description="ID del usuario")

class PasswordResetUpdate(BaseModel):
    """Schema para actualizar un password reset"""
    used: Optional[bool] = None
    
class PasswordResetResponse(PasswordResetBase):
    """Schema para respuesta de password reset"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PasswordResetWithUser(PasswordResetResponse):
    """Schema extendido con información del usuario"""
    user_email: Optional[str] = None
    user_username: Optional[str] = None

class PasswordResetRequest(BaseModel):
    """Schema para solicitar reseteo (público)"""
    email: str = Field(..., description="Email del usuario")

class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reseteo con nueva contraseña (público)"""
    token: str = Field(..., min_length=32, description="Token de reseteo")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_password(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class PasswordResetStats(BaseModel):
    """Schema para estadísticas de password resets"""
    total_requests: int
    used_tokens: int
    expired_tokens: int
    pending_tokens: int
    requests_last_24h: int
    requests_last_week: int