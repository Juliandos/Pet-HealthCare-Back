# ========================================
# app/controllers/notifications.py
# ========================================
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Notification, User, AuditLog
from app.schemas.notifications import NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status

class NotificationController:
    @staticmethod
    def get_all(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[Notification]:
        return db.query(Notification).filter(Notification.owner_id == current_user.id).order_by(desc(Notification.sent_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, notification_id: str, current_user: User) -> Notification:
        notif = db.query(Notification).filter(Notification.id == notification_id, Notification.owner_id == current_user.id).first()
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        return notif
    
    @staticmethod
    def create(db: Session, data: NotificationCreate, current_user: User) -> Notification:
        new_item = Notification(**data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    
    @staticmethod
    def update(db: Session, notification_id: str, data: NotificationUpdate, current_user: User) -> Notification:
        notif = NotificationController.get_by_id(db, notification_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notif, field, value)
        notif.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(notif)
        return notif
    
    @staticmethod
    def delete(db: Session, notification_id: str, current_user: User) -> bool:
        notif = NotificationController.get_by_id(db, notification_id, current_user)
        db.delete(notif)
        db.commit()
        return True


