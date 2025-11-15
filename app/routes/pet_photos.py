# ========================================
# app/routes/pet_photos.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.pet_photos import PetPhotoController
from app.schemas.pet_photos import PetPhotoCreate, PetPhotoUpdate, PetPhotoResponse
from app.models import User

router = APIRouter(prefix="/pet-photos", tags=["Fotos de Mascotas"])

@router.get("/pet/{pet_id}", response_model=list[PetPhotoResponse])
def get_all_pet_photos(
    pet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las fotos de una mascota"""
    return PetPhotoController.get_all(db, current_user, pet_id, skip, limit)

@router.get("/{photo_id}", response_model=PetPhotoResponse)
def get_pet_photo_by_id(photo_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una foto específica"""
    return PetPhotoController.get_by_id(db, photo_id, current_user)

@router.post("/", response_model=PetPhotoResponse, status_code=status.HTTP_201_CREATED)
def create_pet_photo(data: PetPhotoCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva foto de mascota"""
    return PetPhotoController.create(db, data, current_user)

@router.put("/{photo_id}", response_model=PetPhotoResponse)
def update_pet_photo(photo_id: str, data: PetPhotoUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una foto existente"""
    return PetPhotoController.update(db, photo_id, data, current_user)

@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet_photo(photo_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una foto"""
    PetPhotoController.delete(db, photo_id, current_user)
    return None