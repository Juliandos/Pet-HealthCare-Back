# ========================================
# app/routes/notifications.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.middleware.auth import get_db, get_current_active_user, require_role
from app.controllers.notifications import NotificationController
from app.schemas.notifications import NotificationResponse
from app.models import User

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

@router.get("/", response_model=list[NotificationResponse])
def get_all_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las notificaciones del usuario.
    Las notificaciones se crean automáticamente cuando se procesan recordatorios vencidos.
    """
    return NotificationController.get_all(db, current_user, skip, limit)

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_by_id(
    notification_id: str, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """
    Obtiene una notificación específica del usuario.
    Las notificaciones se crean automáticamente cuando se procesan recordatorios vencidos.
    """
    return NotificationController.get_by_id(db, notification_id, current_user)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str, 
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Elimina una notificación (solo admin).
    Las notificaciones se crean automáticamente cuando se procesan recordatorios vencidos.
    """
    NotificationController.delete(db, notification_id, current_user)
    return None


