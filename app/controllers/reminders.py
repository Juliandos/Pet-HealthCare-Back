# ========================================
# app/controllers/reminders.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Reminder, Pet, User, AuditLog
from app.schemas.reminders import ReminderCreate, ReminderUpdate
from fastapi import HTTPException, status

class ReminderController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: Optional[str] = None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Reminder]:
        query = db.query(Reminder).filter(Reminder.owner_id == current_user.id)
        if pet_id:
            query = query.filter(Reminder.pet_id == pet_id)
        if is_active is not None:
            query = query.filter(Reminder.is_active == is_active)
        return query.order_by(Reminder.event_time).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, reminder_id: str, current_user: User) -> Reminder:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.owner_id == current_user.id).first()
        if not reminder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recordatorio no encontrado")
        return reminder
    
    @staticmethod
    def create(db: Session, data: ReminderCreate, current_user: User) -> Reminder:
        # Validar que la mascota existe y pertenece al usuario si se proporciona pet_id
        pet_id_uuid = None
        if data.pet_id:
            try:
                import uuid
                pet_id_uuid = uuid.UUID(data.pet_id) if isinstance(data.pet_id, str) else data.pet_id
                pet = db.query(Pet).filter(Pet.id == pet_id_uuid, Pet.owner_id == current_user.id).first()
                if not pet:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
            except (ValueError, TypeError) as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ID de mascota inválido: {str(e)}")
        
        # Preparar datos para crear el recordatorio
        reminder_data = data.model_dump(exclude={'pet_id'})
        if pet_id_uuid:
            reminder_data['pet_id'] = pet_id_uuid
        
        new_item = Reminder(owner_id=current_user.id, **reminder_data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="REMINDER_CREATED", object_type="Reminder", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, reminder_id: str, data: ReminderUpdate, current_user: User) -> Reminder:
        reminder = ReminderController.get_by_id(db, reminder_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        
        # Manejar conversión de pet_id si se proporciona
        if 'pet_id' in update_data and update_data['pet_id'] is not None:
            try:
                import uuid
                pet_id_uuid = uuid.UUID(update_data['pet_id']) if isinstance(update_data['pet_id'], str) else update_data['pet_id']
                # Validar que la mascota existe y pertenece al usuario
                pet = db.query(Pet).filter(Pet.id == pet_id_uuid, Pet.owner_id == current_user.id).first()
                if not pet:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
                update_data['pet_id'] = pet_id_uuid
            except (ValueError, TypeError) as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ID de mascota inválido: {str(e)}")
        
        for field, value in update_data.items():
            setattr(reminder, field, value)
        reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        
        audit = AuditLog(actor_user_id=current_user.id, action="REMINDER_UPDATED", object_type="Reminder", object_id=reminder.id)
        db.add(audit)
        db.commit()
        return reminder
    
    @staticmethod
    def delete(db: Session, reminder_id: str, current_user: User) -> bool:
        reminder = ReminderController.get_by_id(db, reminder_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="REMINDER_DELETED", object_type="Reminder", object_id=reminder.id)
        db.add(audit)
        db.delete(reminder)
        db.commit()
        return True


