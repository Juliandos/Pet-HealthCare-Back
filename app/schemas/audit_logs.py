# ========================================
# app/schemas/audit_logs.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class AuditLogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100, description="Acción realizada")
    object_type: Optional[str] = Field(None, max_length=100, description="Tipo de objeto afectado")
    object_id: Optional[str] = Field(None, description="ID del objeto afectado")
    meta: Optional[dict[str, Any]] = Field(None, description="Metadatos adicionales en JSON")

class AuditLogCreate(AuditLogBase):
    actor_user_id: str = Field(..., description="ID del usuario que realizó la acción")

class AuditLogUpdate(BaseModel):
    """Los logs de auditoría generalmente no se actualizan, pero dejamos el schema por consistencia"""
    meta: Optional[dict[str, Any]] = None

class AuditLogResponse(AuditLogBase):
    id: str
    actor_user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AuditLogWithUser(AuditLogResponse):
    """Schema extendido con información del usuario actor"""
    actor_username: Optional[str] = None
    actor_email: Optional[str] = None

class AuditLogFilter(BaseModel):
    """Schema para filtros de búsqueda"""
    actor_user_id: Optional[str] = None
    action: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None