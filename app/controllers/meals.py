# ========================================
# app/controllers/meals.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Meal, Pet, User, AuditLog
from app.schemas.meals import MealCreate, MealUpdate
from fastapi import HTTPException, status

class MealController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Meal]:
        query = db.query(Meal).join(Pet).filter(Pet.owner_id == current_user.id)
        if pet_id:
            query = query.filter(Meal.pet_id == pet_id)
        return query.order_by(desc(Meal.meal_time)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, meal_id: str, current_user: User) -> Meal:
        meal = db.query(Meal).join(Pet).filter(Meal.id == meal_id, Pet.owner_id == current_user.id).first()
        if not meal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada")
        return meal
    
    @staticmethod
    def create(db: Session, data: MealCreate, current_user: User) -> Meal:
        pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        
        new_item = Meal(**data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="MEAL_CREATED", object_type="Meal", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, meal_id: str, data: MealUpdate, current_user: User) -> Meal:
        meal = MealController.get_by_id(db, meal_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meal, field, value)
        meal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(meal)
        
        audit = AuditLog(actor_user_id=current_user.id, action="MEAL_UPDATED", object_type="Meal", object_id=meal.id)
        db.add(audit)
        db.commit()
        return meal
    
    @staticmethod
    def delete(db: Session, meal_id: str, current_user: User) -> bool:
        meal = MealController.get_by_id(db, meal_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="MEAL_DELETED", object_type="Meal", object_id=meal.id)
        db.add(audit)
        db.delete(meal)
        db.commit()
        return True


