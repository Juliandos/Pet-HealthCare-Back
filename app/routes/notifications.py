# ========================================
# app/routes/notifications.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.middleware.auth import get_db, get_current_active_user, require_role
from app.controllers.notifications import NotificationController
from app.schemas.notifications import NotificationResponse
from app.models import User, Notification

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

def _notification_to_dict(notification: Notification) -> dict:
    """Convierte un objeto Notification a dict con UUIDs como strings"""
    return {
        'id': str(notification.id),
        'owner_id': str(notification.owner_id) if notification.owner_id else None,
        'reminder_id': str(notification.reminder_id) if notification.reminder_id else None,
        'pet_id': str(notification.pet_id) if notification.pet_id else None,
        'sent_at': notification.sent_at,
        'method': notification.method,
        'status': notification.status,
        'provider_response': notification.provider_response,
        'created_at': notification.created_at,
        'updated_at': notification.updated_at
    }

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
    notifications = NotificationController.get_all(db, current_user, skip, limit)
    return [NotificationResponse(**_notification_to_dict(notif)) for notif in notifications]

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
    notification = NotificationController.get_by_id(db, notification_id, current_user)
    return NotificationResponse(**_notification_to_dict(notification))

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


