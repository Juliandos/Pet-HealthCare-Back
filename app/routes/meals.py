# ========================================
# app/routes/meals.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.meals import MealController
from app.schemas.meals import MealCreate, MealUpdate, MealResponse
from app.models import User

router = APIRouter(prefix="/meals", tags=["Comidas"])

@router.get("/", response_model=list[MealResponse])
def get_all_meals(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las comidas del usuario"""
    meals = MealController.get_all(db, current_user, pet_id, skip, limit)
    return [
        MealResponse(
            id=str(meal.id),
            pet_id=str(meal.pet_id),
            meal_time=meal.meal_time,
            description=meal.description,
            calories=meal.calories,
            plan_id=str(meal.plan_id) if meal.plan_id else None,
            created_at=meal.created_at,
            updated_at=meal.updated_at
        )
        for meal in meals
    ]

@router.get("/{meal_id}", response_model=MealResponse)
def get_meal_by_id(meal_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una comida específica"""
    meal = MealController.get_by_id(db, meal_id, current_user)
    return MealResponse(
        id=str(meal.id),
        pet_id=str(meal.pet_id),
        meal_time=meal.meal_time,
        description=meal.description,
        calories=meal.calories,
        plan_id=str(meal.plan_id) if meal.plan_id else None,
        created_at=meal.created_at,
        updated_at=meal.updated_at
    )

@router.post("/", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
def create_meal(data: MealCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva comida"""
    meal = MealController.create(db, data, current_user)
    return MealResponse(
        id=str(meal.id),
        pet_id=str(meal.pet_id),
        meal_time=meal.meal_time,
        description=meal.description,
        calories=meal.calories,
        plan_id=str(meal.plan_id) if meal.plan_id else None,
        created_at=meal.created_at,
        updated_at=meal.updated_at
    )

@router.put("/{meal_id}", response_model=MealResponse)
def update_meal(meal_id: str, data: MealUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una comida existente"""
    meal = MealController.update(db, meal_id, data, current_user)
    return MealResponse(
        id=str(meal.id),
        pet_id=str(meal.pet_id),
        meal_time=meal.meal_time,
        description=meal.description,
        calories=meal.calories,
        plan_id=str(meal.plan_id) if meal.plan_id else None,
        created_at=meal.created_at,
        updated_at=meal.updated_at
    )

@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una comida"""
    MealController.delete(db, meal_id, current_user)
    return None


