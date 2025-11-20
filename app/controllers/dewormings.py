# ========================================
# app/controllers/dewormings.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Deworming, Pet, User, AuditLog
from app.schemas.dewormings import DewormingCreate, DewormingUpdate
from fastapi import HTTPException, status

class DewormingController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Deworming]:
        query = db.query(Deworming).join(Pet).filter(Pet.owner_id == current_user.id)
        if pet_id:
            query = query.filter(Deworming.pet_id == pet_id)
        return query.order_by(desc(Deworming.date_administered)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, deworming_id: str, current_user: User) -> Deworming:
        deworming = db.query(Deworming).join(Pet).filter(Deworming.id == deworming_id, Pet.owner_id == current_user.id).first()
        if not deworming:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Desparasitación no encontrada")
        return deworming
    
    @staticmethod
    def create(db: Session, data: DewormingCreate, current_user: User) -> Deworming:
        pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        
        new_item = Deworming(**data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="DEWORMING_CREATED", object_type="Deworming", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, deworming_id: str, data: DewormingUpdate, current_user: User) -> Deworming:
        deworming = DewormingController.get_by_id(db, deworming_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deworming, field, value)
        deworming.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(deworming)
        
        audit = AuditLog(actor_user_id=current_user.id, action="DEWORMING_UPDATED", object_type="Deworming", object_id=deworming.id)
        db.add(audit)
        db.commit()
        return deworming
    
    @staticmethod
    def delete(db: Session, deworming_id: str, current_user: User) -> bool:
        deworming = DewormingController.get_by_id(db, deworming_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="DEWORMING_DELETED", object_type="Deworming", object_id=deworming.id)
        db.add(audit)
        db.delete(deworming)
        db.commit()
        return True
