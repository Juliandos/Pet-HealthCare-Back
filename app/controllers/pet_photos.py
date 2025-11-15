# ========================================
# app/controllers/pet_photos.py
# ========================================
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models import PetPhoto, Pet, User, AuditLog
from app.schemas.pet_photos import PetPhotoCreate, PetPhotoUpdate
from fastapi import HTTPException, status

class PetPhotoController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: str, skip: int = 0, limit: int = 100) -> List[PetPhoto]:
        pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        return db.query(PetPhoto).filter(PetPhoto.pet_id == pet_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, photo_id: str, current_user: User) -> PetPhoto:
        photo = db.query(PetPhoto).join(Pet).filter(PetPhoto.id == photo_id, Pet.owner_id == current_user.id).first()
        if not photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto no encontrada")
        return photo
    
    @staticmethod
    def create(db: Session, data: PetPhotoCreate, current_user: User) -> PetPhoto:
        pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        
        new_item = PetPhoto(**data.model_dump(exclude={'data'}))
        if data.data:
            new_item.data = data.data
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="PET_PHOTO_CREATED", object_type="PetPhoto", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, photo_id: str, data: PetPhotoUpdate, current_user: User) -> PetPhoto:
        photo = PetPhotoController.get_by_id(db, photo_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(photo, field, value)
        photo.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(photo)
        return photo
    
    @staticmethod
    def delete(db: Session, photo_id: str, current_user: User) -> bool:
        photo = PetPhotoController.get_by_id(db, photo_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="PET_PHOTO_DELETED", object_type="PetPhoto", object_id=photo.id)
        db.add(audit)
        db.delete(photo)
        db.commit()
        return True