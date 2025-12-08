# ========================================
# app/controllers/reminders.py
# ========================================
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.models import Reminder, Pet, User, AuditLog, Notification
from app.schemas.reminders import ReminderCreate, ReminderUpdate
from app.services.email_service import EmailService
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

    @staticmethod
    def process_due_reminders(db: Session) -> dict:
        """
        Procesa recordatorios vencidos: crea notificaciones y envía correos
        
        Args:
            db: Sesión de base de datos
        
        Returns:
            dict: Resumen de recordatorios procesados
        """
        now = datetime.utcnow()
        # Buscar recordatorios activos que ya vencieron (event_time <= ahora)
        # Procesamos recordatorios de las últimas 24 horas para evitar procesar todos los antiguos
        # y para manejar recordatorios recurrentes
        one_day_ago = now - timedelta(days=1)
        
        due_reminders = db.query(Reminder).filter(
            and_(
                Reminder.is_active == True,
                Reminder.event_time <= now,
                Reminder.event_time >= one_day_ago  # Solo procesar recordatorios del último día
            )
        ).all()
        
        processed_count = 0
        notifications_created = 0
        emails_sent = 0
        errors = []
        
        for reminder in due_reminders:
            try:
                # Verificar si ya existe una notificación para este recordatorio en las últimas 2 horas
                # para evitar duplicados (permite un margen de tiempo para procesamiento)
                two_hours_ago = now - timedelta(hours=2)
                existing_notification = db.query(Notification).filter(
                    and_(
                        Notification.reminder_id == reminder.id,
                        Notification.sent_at >= two_hours_ago
                    )
                ).first()
                
                if existing_notification:
                    # Ya se procesó este recordatorio recientemente
                    continue
                
                # Obtener el usuario propietario
                user = db.query(User).filter(User.id == reminder.owner_id).first()
                if not user:
                    errors.append(f"Usuario no encontrado para recordatorio {reminder.id}")
                    continue
                
                # Obtener la mascota si existe
                pet = None
                pet_name = None
                if reminder.pet_id:
                    pet = db.query(Pet).filter(Pet.id == reminder.pet_id).first()
                    if pet:
                        pet_name = pet.name
                
                # Crear la notificación
                notification = Notification(
                    reminder_id=reminder.id,
                    owner_id=reminder.owner_id,
                    pet_id=reminder.pet_id,
                    sent_at=now,
                    method="email" if reminder.notify_by_email else "in_app",
                    status="pending"
                )
                db.add(notification)
                db.flush()  # Para obtener el ID de la notificación
                
                # Enviar correo si está habilitado
                email_sent = False
                if reminder.notify_by_email and user.email:
                    try:
                        email_sent = EmailService.send_reminder_email(
                            email=user.email,
                            username=user.username or user.full_name or "Usuario",
                            reminder_title=reminder.title,
                            reminder_description=reminder.description,
                            pet_name=pet_name
                        )
                        
                        if email_sent:
                            notification.status = "sent"
                            notification.provider_response = {"email_sent": True, "sent_at": now.isoformat()}
                            emails_sent += 1
                        else:
                            notification.status = "failed"
                            notification.provider_response = {"email_sent": False, "error": "Error al enviar email"}
                    except Exception as e:
                        notification.status = "failed"
                        notification.provider_response = {"email_sent": False, "error": str(e)}
                        errors.append(f"Error enviando email para recordatorio {reminder.id}: {str(e)}")
                else:
                    # Si no se envía email, solo notificación in-app
                    notification.status = "sent"
                
                # Si solo es notificación in-app
                if not reminder.notify_by_email and reminder.notify_in_app:
                    notification.status = "sent"
                
                db.commit()
                notifications_created += 1
                processed_count += 1
                
                # Log de auditoría
                audit = AuditLog(
                    actor_user_id=reminder.owner_id,
                    action="REMINDER_PROCESSED",
                    object_type="Reminder",
                    object_id=reminder.id,
                    meta={"notification_id": str(notification.id), "email_sent": email_sent}
                )
                db.add(audit)
                db.commit()
                
            except Exception as e:
                db.rollback()
                error_msg = f"Error procesando recordatorio {reminder.id}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return {
            "processed_count": processed_count,
            "notifications_created": notifications_created,
            "emails_sent": emails_sent,
            "errors": errors,
            "timestamp": now.isoformat()
        }


