# ========================================
# app/controllers/notifications.py
# ========================================
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Notification, User, AuditLog
from fastapi import HTTPException, status

class NotificationController:
    """
    Controlador para notificaciones.
    Las notificaciones se crean automáticamente cuando se procesan recordatorios vencidos.
    Los usuarios solo pueden ver sus notificaciones y los admins pueden eliminarlas.
    """
    
    @staticmethod
    def get_all(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[Notification]:
        """
        Obtiene todas las notificaciones del usuario actual.
        Las notificaciones se ordenan por fecha de envío descendente (más recientes primero).
        """
        return db.query(Notification).filter(Notification.owner_id == current_user.id).order_by(desc(Notification.sent_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, notification_id: str, current_user: User) -> Notification:
        """
        Obtiene una notificación específica del usuario actual.
        """
        notif = db.query(Notification).filter(Notification.id == notification_id, Notification.owner_id == current_user.id).first()
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        return notif
    
    @staticmethod
    def delete(db: Session, notification_id: str, current_user: User) -> bool:
        """
        Elimina una notificación (solo admin).
        Se registra en el log de auditoría.
        """
        # Los admins pueden eliminar cualquier notificación
        notif = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        
        # Registrar en auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="NOTIFICATION_DELETED",
            object_type="Notification",
            object_id=notif.id,
            meta={"owner_id": str(notif.owner_id)}
        )
        db.add(audit)
        db.delete(notif)
        db.commit()
        return True


