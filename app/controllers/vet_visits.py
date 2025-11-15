# ========================================
# app/controllers/vet_visits.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import VetVisit, Pet, User, AuditLog
from app.schemas.vet_visits import VetVisitCreate, VetVisitUpdate
from fastapi import HTTPException, status

class VetVisitController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[VetVisit]:
        query = db.query(VetVisit).join(Pet).filter(Pet.owner_id == current_user.id)
        if pet_id:
            query = query.filter(VetVisit.pet_id == pet_id)
        return query.order_by(desc(VetVisit.visit_date)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, visit_id: str, current_user: User) -> VetVisit:
        visit = db.query(VetVisit).join(Pet).filter(VetVisit.id == visit_id, Pet.owner_id == current_user.id).first()
        if not visit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visita veterinaria no encontrada")
        return visit
    
    @staticmethod
    def create(db: Session, data: VetVisitCreate, current_user: User) -> VetVisit:
        pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        
        new_item = VetVisit(**data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="VET_VISIT_CREATED", object_type="VetVisit", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, visit_id: str, data: VetVisitUpdate, current_user: User) -> VetVisit:
        visit = VetVisitController.get_by_id(db, visit_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(visit, field, value)
        visit.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(visit)
        
        audit = AuditLog(actor_user_id=current_user.id, action="VET_VISIT_UPDATED", object_type="VetVisit", object_id=visit.id)
        db.add(audit)
        db.commit()
        return visit
    
    @staticmethod
    def delete(db: Session, visit_id: str, current_user: User) -> bool:
        visit = VetVisitController.get_by_id(db, visit_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="VET_VISIT_DELETED", object_type="VetVisit", object_id=visit.id)
        db.add(audit)
        db.delete(visit)
        db.commit()
        return True


