from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserRegister(BaseModel):
    """Schema para registro de usuario - Solo email y password son requeridos"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str | None = Field(None, min_length=3, max_length=50)
    full_name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = None
    timezone: str | None = None
    
    @validator('password')
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
    
    @validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v

class UserLogin(BaseModel):
    """Schema para login de usuario"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Schema para respuesta de tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    """Schema para refrescar token"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Schema para solicitar reseteo de contraseña"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema para resetear contraseña"""
    token: str
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

class EmailVerification(BaseModel):
    """Schema para verificar email"""
    token: str

class UserProfile(BaseModel):
    """Schema para perfil de usuario"""
    id: str
    username: str | None
    email: str
    full_name: str | None
    phone: str | None
    timezone: str | None
    role: str
    email_verified: bool
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True