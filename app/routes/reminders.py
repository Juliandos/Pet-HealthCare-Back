# ========================================
# app/routes/reminders.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.reminders import ReminderController
from app.schemas.reminders import ReminderCreate, ReminderUpdate, ReminderResponse
from app.models import User

router = APIRouter(prefix="/reminders", tags=["Recordatorios"])

@router.get("/", response_model=list[ReminderResponse])
def get_all_reminders(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los recordatorios del usuario"""
    return ReminderController.get_all(db, current_user, pet_id, is_active, skip, limit)

@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder_by_id(reminder_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene un recordatorio específico"""
    return ReminderController.get_by_id(db, reminder_id, current_user)

@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(data: ReminderCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea un nuevo recordatorio"""
    return ReminderController.create(db, data, current_user)

@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: str, data: ReminderUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza un recordatorio existente"""
    return ReminderController.update(db, reminder_id, data, current_user)

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina un recordatorio"""
    ReminderController.delete(db, reminder_id, current_user)
    return None


