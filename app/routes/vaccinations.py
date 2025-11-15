# ========================================
# app/routes/vaccinations.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.vaccinations import VaccinationController
from app.schemas.vaccinations import VaccinationCreate, VaccinationUpdate, VaccinationResponse
from app.models import User

router = APIRouter(prefix="/vaccinations", tags=["Vacunaciones"])

@router.get("/", response_model=list[VaccinationResponse])
def get_all_vaccinations(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las vacunaciones del usuario (opcionalmente filtradas por mascota)"""
    return VaccinationController.get_all_vaccinations(db, current_user, pet_id, skip, limit)

@router.get("/{vaccination_id}", response_model=VaccinationResponse)
def get_vaccination_by_id(vaccination_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una vacunación específica por ID"""
    return VaccinationController.get_vaccination_by_id(db, vaccination_id, current_user)

@router.post("/", response_model=VaccinationResponse, status_code=status.HTTP_201_CREATED)
def create_vaccination(data: VaccinationCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva vacunación"""
    return VaccinationController.create_vaccination(db, data, current_user)

@router.put("/{vaccination_id}", response_model=VaccinationResponse)
def update_vaccination(vaccination_id: str, data: VaccinationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una vacunación existente"""
    return VaccinationController.update_vaccination(db, vaccination_id, data, current_user)

@router.delete("/{vaccination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vaccination(vaccination_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una vacunación"""
    VaccinationController.delete_vaccination(db, vaccination_id, current_user)
    return None


