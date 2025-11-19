# ========================================
# app/routes/nutrition_plans.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.nutrition_plans import NutritionPlanController
from app.schemas.nutrition_plans import (
    NutritionPlanCreate,
    NutritionPlanUpdate,
    NutritionPlanResponse,
    NutritionPlanWithMeals,
    NutritionPlanSummary
)
from app.models import User

router = APIRouter(prefix="/nutrition-plans", tags=["Planes de Nutrición"])

# ============================================
# ENDPOINTS CRUD BÁSICOS
# ============================================

@router.get("/", response_model=List[NutritionPlanResponse])
def get_all_nutrition_plans(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota específica"),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los planes de nutrición del usuario
    
    Opcionalmente se puede filtrar por mascota específica
    """
    plans = NutritionPlanController.get_all(
        db=db,
        current_user=current_user,
        pet_id=pet_id,
        skip=skip,
        limit=limit
    )
    
    return [
        NutritionPlanResponse(
            id=str(plan.id),
            pet_id=str(plan.pet_id),
            name=plan.name,
            description=plan.description,
            calories_per_day=plan.calories_per_day,
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )
        for plan in plans
    ]

@router.get("/summary", response_model=List[NutritionPlanSummary])
def get_plans_summary(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de planes de nutrición (solo datos básicos)
    
    Útil para listados rápidos sin información detallada
    """
    plans = NutritionPlanController.get_all(
        db=db,
        current_user=current_user,
        pet_id=pet_id,
        skip=0,
        limit=100
    )
    
    return [
        NutritionPlanSummary(
            id=str(plan.id),
            pet_id=str(plan.pet_id),
            name=plan.name,
            calories_per_day=plan.calories_per_day
        )
        for plan in plans
    ]

@router.get("/{plan_id}", response_model=NutritionPlanResponse)
def get_nutrition_plan_by_id(
    plan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un plan de nutrición específico por ID
    
    Solo puedes ver planes de tus propias mascotas
    """
    plan = NutritionPlanController.get_by_id(
        db=db,
        plan_id=plan_id,
        current_user=current_user
    )
    
    return NutritionPlanResponse(
        id=str(plan.id),
        pet_id=str(plan.pet_id),
        name=plan.name,
        description=plan.description,
        calories_per_day=plan.calories_per_day,
        created_at=plan.created_at,
        updated_at=plan.updated_at
    )

@router.post("/", response_model=NutritionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_nutrition_plan(
    data: NutritionPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo plan de nutrición
    
    **Campos requeridos:**
    - `pet_id`: ID de la mascota
    - `name`: Nombre del plan
    
    **Campos opcionales:**
    - `description`: Descripción detallada
    - `calories_per_day`: Calorías diarias recomendadas
    
    **Ejemplo:**
    ```json
    {
        "pet_id": "uuid-de-la-mascota",
        "name": "Plan de Pérdida de Peso",
        "description": "Plan bajo en calorías para reducir peso gradualmente",
        "calories_per_day": 800
    }
    ```
    """
    plan = NutritionPlanController.create(
        db=db,
        data=data,
        current_user=current_user
    )
    
    return NutritionPlanResponse(
        id=str(plan.id),
        pet_id=str(plan.pet_id),
        name=plan.name,
        description=plan.description,
        calories_per_day=plan.calories_per_day,
        created_at=plan.created_at,
        updated_at=plan.updated_at
    )

@router.put("/{plan_id}", response_model=NutritionPlanResponse)
def update_nutrition_plan(
    plan_id: str,
    data: NutritionPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza un plan de nutrición existente
    
    Solo se actualizarán los campos proporcionados
    """
    plan = NutritionPlanController.update(
        db=db,
        plan_id=plan_id,
        data=data,
        current_user=current_user
    )
    
    return NutritionPlanResponse(
        id=str(plan.id),
        pet_id=str(plan.pet_id),
        name=plan.name,
        description=plan.description,
        calories_per_day=plan.calories_per_day,
        created_at=plan.created_at,
        updated_at=plan.updated_at
    )

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nutrition_plan(
    plan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un plan de nutrición
    
    **Nota:** Esto también afectará las comidas que tengan este plan_id
    """
    NutritionPlanController.delete(
        db=db,
        plan_id=plan_id,
        current_user=current_user
    )
    
    return None

# ============================================
# ENDPOINTS CON ESTADÍSTICAS
# ============================================

@router.get("/{plan_id}/stats", response_model=NutritionPlanWithMeals)
def get_plan_with_statistics(
    plan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un plan de nutrición con estadísticas de comidas
    
    Incluye:
    - Total de comidas registradas bajo este plan
    - Promedio de calorías por comida
    """
    stats = NutritionPlanController.get_plan_with_stats(
        db=db,
        plan_id=plan_id,
        current_user=current_user
    )
    
    return NutritionPlanWithMeals(**stats)

# ============================================
# ENDPOINTS ADICIONALES ÚTILES
# ============================================

@router.get("/pet/{pet_id}/active", response_model=NutritionPlanResponse)
def get_active_plan_for_pet(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el plan de nutrición activo (más reciente) para una mascota
    
    Útil para saber qué plan está siguiendo actualmente la mascota
    """
    plan = NutritionPlanController.get_active_plan_for_pet(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    if not plan:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta mascota no tiene planes de nutrición"
        )
    
    return NutritionPlanResponse(
        id=str(plan.id),
        pet_id=str(plan.pet_id),
        name=plan.name,
        description=plan.description,
        calories_per_day=plan.calories_per_day,
        created_at=plan.created_at,
        updated_at=plan.updated_at
    )

@router.post("/{plan_id}/duplicate", response_model=NutritionPlanResponse, status_code=status.HTTP_201_CREATED)
def duplicate_nutrition_plan(
    plan_id: str,
    new_pet_id: Optional[str] = Query(None, description="ID de la nueva mascota (opcional, usa la misma si no se proporciona)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Duplica un plan de nutrición existente
    
    Útil para:
    - Reutilizar un plan en otra mascota
    - Crear variaciones de un plan existente
    
    **Parámetros:**
    - `plan_id`: ID del plan a duplicar
    - `new_pet_id`: (Opcional) ID de la mascota destino. Si no se proporciona, usa la misma mascota
    
    El plan duplicado tendrá el mismo contenido pero con el nombre "(copia)" al final
    """
    new_plan = NutritionPlanController.duplicate_plan(
        db=db,
        plan_id=plan_id,
        new_pet_id=new_pet_id,
        current_user=current_user
    )
    
    return NutritionPlanResponse(
        id=str(new_plan.id),
        pet_id=str(new_plan.pet_id),
        name=new_plan.name,
        description=new_plan.description,
        calories_per_day=new_plan.calories_per_day,
        created_at=new_plan.created_at,
        updated_at=new_plan.updated_at
    )

@router.get("/pet/{pet_id}/history", response_model=List[NutritionPlanSummary])
def get_nutrition_history_for_pet(
    pet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial completo de planes de nutrición de una mascota
    
    Los planes se ordenan del más reciente al más antiguo
    """
    plans = NutritionPlanController.get_all(
        db=db,
        current_user=current_user,
        pet_id=pet_id,
        skip=skip,
        limit=limit
    )
    
    return [
        NutritionPlanSummary(
            id=str(plan.id),
            pet_id=str(plan.pet_id),
            name=plan.name,
            calories_per_day=plan.calories_per_day
        )
        for plan in plans
    ]