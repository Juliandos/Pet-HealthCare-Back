# ========================================
# app/controllers/nutrition_plans.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import NutritionPlan, Pet, User, AuditLog
from app.schemas.nutrition_plans import NutritionPlanCreate, NutritionPlanUpdate
from fastapi import HTTPException, status

class NutritionPlanController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[NutritionPlan]:
        query = db.query(NutritionPlan).join(Pet).filter(Pet.owner_id == current_user.id)
        if pet_id:
            query = query.filter(NutritionPlan.pet_id == pet_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, plan_id: str, current_user: User) -> NutritionPlan:
        plan = db.query(NutritionPlan).join(Pet).filter(NutritionPlan.id == plan_id, Pet.owner_id == current_user.id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan de nutrición no encontrado")
        return plan
    
    @staticmethod
    def create(db: Session, data: NutritionPlanCreate, current_user: User) -> NutritionPlan:
        pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        
        new_item = NutritionPlan(**data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="NUTRITION_PLAN_CREATED", object_type="NutritionPlan", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, plan_id: str, data: NutritionPlanUpdate, current_user: User) -> NutritionPlan:
        plan = NutritionPlanController.get_by_id(db, plan_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)
        plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(plan)
        
        audit = AuditLog(actor_user_id=current_user.id, action="NUTRITION_PLAN_UPDATED", object_type="NutritionPlan", object_id=plan.id)
        db.add(audit)
        db.commit()
        return plan
    
    @staticmethod
    def delete(db: Session, plan_id: str, current_user: User) -> bool:
        plan = NutritionPlanController.get_by_id(db, plan_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="NUTRITION_PLAN_DELETED", object_type="NutritionPlan", object_id=plan.id)
        db.add(audit)
        db.delete(plan)
        db.commit()
        return True


