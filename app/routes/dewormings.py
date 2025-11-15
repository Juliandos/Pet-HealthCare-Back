# ========================================
# app/routes/dewormings.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.dewormings import DewormingController
from app.schemas.dewormings import DewormingCreate, DewormingUpdate, DewormingResponse
from app.models import User

router = APIRouter(prefix="/dewormings", tags=["Desparasitaciones"])

@router.get("/", response_model=list[DewormingResponse])
def get_all_dewormings(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las desparasitaciones del usuario"""
    return DewormingController.get_all(db, current_user, pet_id, skip, limit)

@router.get("/{deworming_id}", response_model=DewormingResponse)
def get_deworming_by_id(deworming_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una desparasitación específica"""
    return DewormingController.get_by_id(db, deworming_id, current_user)

@router.post("/", response_model=DewormingResponse, status_code=status.HTTP_201_CREATED)
def create_deworming(data: DewormingCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva desparasitación"""
    return DewormingController.create(db, data, current_user)

@router.put("/{deworming_id}", response_model=DewormingResponse)
def update_deworming(deworming_id: str, data: DewormingUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una desparasitación existente"""
    return DewormingController.update(db, deworming_id, data, current_user)

@router.delete("/{deworming_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deworming(deworming_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una desparasitación"""
    DewormingController.delete(db, deworming_id, current_user)
    return None


