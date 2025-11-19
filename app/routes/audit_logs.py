# ========================================
# app/routes/audit_logs.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.middleware.auth import get_db, get_current_active_user, require_role
from app.controllers.audit_logs import AuditLogController
from app.schemas.audit_logs import (
    AuditLogResponse,
    AuditLogWithUser,
    AuditLogFilter,
    AuditLogCreate
)
from app.models import User

router = APIRouter(prefix="/audit-logs", tags=["Logs de Auditoría"])

# ============================================
# ENDPOINTS BÁSICOS
# ============================================

@router.get("/", response_model=List[AuditLogWithUser])
def get_all_audit_logs(
    actor_user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    action: Optional[str] = Query(None, description="Filtrar por acción"),
    object_type: Optional[str] = Query(None, description="Filtrar por tipo de objeto"),
    object_id: Optional[str] = Query(None, description="Filtrar por ID de objeto"),
    date_from: Optional[datetime] = Query(None, description="Desde fecha"),
    date_to: Optional[datetime] = Query(None, description="Hasta fecha"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los logs de auditoría con filtros
    
    **Permisos:**
    - **Admin:** Puede ver todos los logs
    - **Usuario:** Solo ve sus propios logs
    
    **Filtros disponibles:**
    - `actor_user_id`: ID del usuario que realizó la acción
    - `action`: Nombre de la acción (búsqueda parcial)
    - `object_type`: Tipo de objeto afectado
    - `object_id`: ID específico del objeto
    - `date_from`: Logs desde esta fecha
    - `date_to`: Logs hasta esta fecha
    """
    filters = AuditLogFilter(
        actor_user_id=actor_user_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        date_from=date_from,
        date_to=date_to
    )
    
    logs = AuditLogController.get_all(
        db=db,
        current_user=current_user,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    # Enriquecer con información del usuario
    enriched_logs = []
    for log in logs:
        log_dict = AuditLogWithUser(
            id=str(log.id),
            actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
            action=log.action,
            object_type=log.object_type,
            object_id=str(log.object_id) if log.object_id else None,
            meta=log.meta,
            created_at=log.created_at,
            updated_at=log.updated_at,
            actor_username=log.actor.username if log.actor else None,
            actor_email=log.actor.email if log.actor else None
        )
        enriched_logs.append(log_dict)
    
    return enriched_logs

@router.get("/my-activity", response_model=List[AuditLogResponse])
def get_my_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene toda la actividad del usuario autenticado
    
    Útil para que los usuarios vean su propio historial de acciones
    """
    logs = AuditLogController.get_user_activity(
        db=db,
        user_id=str(current_user.id),
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    
    return [
        AuditLogResponse(
            id=str(log.id),
            actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
            action=log.action,
            object_type=log.object_type,
            object_id=str(log.object_id) if log.object_id else None,
            meta=log.meta,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]

@router.get("/{audit_log_id}", response_model=AuditLogWithUser)
def get_audit_log_by_id(
    audit_log_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un log de auditoría específico por ID
    
    **Permisos:**
    - **Admin:** Puede ver cualquier log
    - **Usuario:** Solo puede ver sus propios logs
    """
    log = AuditLogController.get_by_id(
        db=db,
        audit_log_id=audit_log_id,
        current_user=current_user
    )
    
    return AuditLogWithUser(
        id=str(log.id),
        actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
        action=log.action,
        object_type=log.object_type,
        object_id=str(log.object_id) if log.object_id else None,
        meta=log.meta,
        created_at=log.created_at,
        updated_at=log.updated_at,
        actor_username=log.actor.username if log.actor else None,
        actor_email=log.actor.email if log.actor else None
    )

# ============================================
# ENDPOINTS DE ADMINISTRACIÓN (solo admin)
# ============================================

@router.get("/user/{user_id}/activity", response_model=List[AuditLogResponse])
def get_user_activity(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN o propio usuario]** Obtiene toda la actividad de un usuario específico
    
    Muestra el historial completo de acciones realizadas por el usuario
    """
    logs = AuditLogController.get_user_activity(
        db=db,
        user_id=user_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    
    return [
        AuditLogResponse(
            id=str(log.id),
            actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
            action=log.action,
            object_type=log.object_type,
            object_id=str(log.object_id) if log.object_id else None,
            meta=log.meta,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]

@router.get("/object/{object_type}/{object_id}/history", response_model=List[AuditLogWithUser])
def get_object_history(
    object_type: str,
    object_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene el historial completo de cambios de un objeto
    
    Útil para auditoría y troubleshooting
    
    **Ejemplo:** `/audit-logs/object/Pet/550e8400-e29b-41d4-a716-446655440000/history`
    """
    logs = AuditLogController.get_object_history(
        db=db,
        object_type=object_type,
        object_id=object_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    
    return [
        AuditLogWithUser(
            id=str(log.id),
            actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
            action=log.action,
            object_type=log.object_type,
            object_id=str(log.object_id) if log.object_id else None,
            meta=log.meta,
            created_at=log.created_at,
            updated_at=log.updated_at,
            actor_username=log.actor.username if log.actor else None,
            actor_email=log.actor.email if log.actor else None
        )
        for log in logs
    ]

@router.get("/stats/overview")
def get_audit_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene estadísticas generales de auditoría
    
    Incluye:
    - Total de logs
    - Logs de hoy
    - Top 10 acciones más frecuentes
    - Top 10 tipos de objetos más modificados
    - Top 10 usuarios más activos
    """
    return AuditLogController.get_statistics(db=db, current_user=current_user)

@router.delete("/purge")
def purge_old_audit_logs(
    days: int = Query(..., ge=1, le=3650, description="Eliminar logs más antiguos que X días"),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Elimina logs de auditoría antiguos
    
    Útil para mantenimiento de base de datos y cumplimiento de GDPR
    
    **⚠️ ADVERTENCIA:** Esta acción es irreversible
    
    **Parámetros:**
    - `days`: Eliminar logs más antiguos que este número de días (mínimo 1, máximo 3650)
    
    **Ejemplo:** `/audit-logs/purge?days=365` elimina logs de hace más de 1 año
    """
    deleted_count = AuditLogController.delete_old_logs(
        db=db,
        days=days,
        current_user=current_user
    )
    
    return {
        "message": f"Se eliminaron {deleted_count} logs de auditoría",
        "deleted_count": deleted_count,
        "days_older_than": days
    }

@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log_manual(
    data: AuditLogCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Crea un log de auditoría manualmente
    
    **Nota:** Los logs normalmente se crean automáticamente por el sistema.
    Este endpoint es para casos especiales o correcciones.
    """
    log = AuditLogController.create(db=db, data=data)
    
    return AuditLogResponse(
        id=str(log.id),
        actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
        action=log.action,
        object_type=log.object_type,
        object_id=str(log.object_id) if log.object_id else None,
        meta=log.meta,
        created_at=log.created_at,
        updated_at=log.updated_at
    )