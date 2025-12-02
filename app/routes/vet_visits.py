# ========================================
# app/routes/vet_visits.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.vet_visits import VetVisitController
from app.schemas.vet_visits import VetVisitCreate, VetVisitUpdate, VetVisitResponse
from app.models import User

router = APIRouter(prefix="/vet-visits", tags=["Visitas Veterinarias"])

@router.get("/", response_model=list[VetVisitResponse])
def get_all_vet_visits(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las visitas veterinarias del usuario"""
    visits = VetVisitController.get_all(db, current_user, pet_id, skip, limit)
    return [
        VetVisitResponse(
            id=str(visit.id),
            pet_id=str(visit.pet_id),
            visit_date=visit.visit_date,
            reason=visit.reason,
            diagnosis=visit.diagnosis,
            treatment=visit.treatment,
            follow_up_date=visit.follow_up_date,
            veterinarian=visit.veterinarian,
            documents_id=visit.documents_id,
            created_at=visit.created_at,
            updated_at=visit.updated_at
        )
        for visit in visits
    ]

@router.get("/{visit_id}", response_model=VetVisitResponse)
def get_vet_visit_by_id(visit_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una visita veterinaria específica"""
    visit = VetVisitController.get_by_id(db, visit_id, current_user)
    return VetVisitResponse(
        id=str(visit.id),
        pet_id=str(visit.pet_id),
        visit_date=visit.visit_date,
        reason=visit.reason,
        diagnosis=visit.diagnosis,
        treatment=visit.treatment,
        follow_up_date=visit.follow_up_date,
        veterinarian=visit.veterinarian,
        documents_id=visit.documents_id,
        created_at=visit.created_at,
        updated_at=visit.updated_at
    )

@router.post("/", response_model=VetVisitResponse, status_code=status.HTTP_201_CREATED)
def create_vet_visit(data: VetVisitCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva visita veterinaria"""
    visit = VetVisitController.create(db, data, current_user)
    return VetVisitResponse(
        id=str(visit.id),
        pet_id=str(visit.pet_id),
        visit_date=visit.visit_date,
        reason=visit.reason,
        diagnosis=visit.diagnosis,
        treatment=visit.treatment,
        follow_up_date=visit.follow_up_date,
        veterinarian=visit.veterinarian,
        documents_id=visit.documents_id,
        created_at=visit.created_at,
        updated_at=visit.updated_at
    )

@router.put("/{visit_id}", response_model=VetVisitResponse)
def update_vet_visit(visit_id: str, data: VetVisitUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una visita veterinaria existente"""
    visit = VetVisitController.update(db, visit_id, data, current_user)
    return VetVisitResponse(
        id=str(visit.id),
        pet_id=str(visit.pet_id),
        visit_date=visit.visit_date,
        reason=visit.reason,
        diagnosis=visit.diagnosis,
        treatment=visit.treatment,
        follow_up_date=visit.follow_up_date,
        veterinarian=visit.veterinarian,
        documents_id=visit.documents_id,
        created_at=visit.created_at,
        updated_at=visit.updated_at
    )

@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vet_visit(visit_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una visita veterinaria"""
    VetVisitController.delete(db, visit_id, current_user)
    return None


