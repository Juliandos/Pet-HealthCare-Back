from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    """Schema base para usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    timezone: Optional[str] = "UTC"
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v

class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    timezone: Optional[str] = None
    role: Optional[str] = None  # Solo admin puede cambiar esto
    email_verified: Optional[bool] = None  # Solo admin puede cambiar esto
    is_active: Optional[bool] = None  # Solo admin puede cambiar esto
    
    @validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v

class UserChangePassword(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserResponse(BaseModel):
    """Schema para respuesta de usuario (sin datos sensibles)"""
    id: str
    username: str
    email: str
    full_name: str
    phone: Optional[str]
    timezone: Optional[str]
    role: str
    email_verified: bool
    is_active: bool
    last_login_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UserStatistics(BaseModel):
    """Schema para estadísticas del usuario"""
    user_id: str
    username: str
    total_pets: int
    total_reminders: int
    active_reminders: int
    total_notifications: int
    account_created: str
    last_login: Optional[str]