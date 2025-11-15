# ========================================
# app/routes/nutrition_plans.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.nutrition_plans import NutritionPlanController
from app.schemas.nutrition_plans import NutritionPlanCreate, NutritionPlanUpdate, NutritionPlanResponse
from app.models import User

router = APIRouter(prefix="/nutrition-plans", tags=["Planes de Nutrición"])

@router.get("/", response_model=list[NutritionPlanResponse])
def get_all_nutrition_plans(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los planes de nutrición del usuario"""
    return NutritionPlanController.get_all(db, current_user, pet_id, skip, limit)

@router.get("/{plan_id}", response_model=NutritionPlanResponse)
def get_nutrition_plan_by_id(plan_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene un plan de nutrición específico"""
    return NutritionPlanController.get_by_id(db, plan_id, current_user)

@router.post("/", response_model=NutritionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_nutrition_plan(data: NutritionPlanCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea un nuevo plan de nutrición"""
    return NutritionPlanController.create(db, data, current_user)

@router.put("/{plan_id}", response_model=NutritionPlanResponse)
def update_nutrition_plan(plan_id: str, data: NutritionPlanUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza un plan de nutrición existente"""
    return NutritionPlanController.update(db, plan_id, data, current_user)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nutrition_plan(plan_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina un plan de nutrición"""
    NutritionPlanController.delete(db, plan_id, current_user)
    return None


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
    return MealController.get_all(db, current_user, pet_id, skip, limit)

@router.get("/{meal_id}", response_model=MealResponse)
def get_meal_by_id(meal_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una comida específica"""
    return MealController.get_by_id(db, meal_id, current_user)

@router.post("/", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
def create_meal(data: MealCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva comida"""
    return MealController.create(db, data, current_user)

@router.put("/{meal_id}", response_model=MealResponse)
def update_meal(meal_id: str, data: MealUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una comida existente"""
    return MealController.update(db, meal_id, data, current_user)

@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una comida"""
    MealController.delete(db, meal_id, current_user)
    return None


# ========================================
# app/routes/reminders.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.reminders import ReminderController
from app.schemas.reminders import ReminderCreate, ReminderUpdate, ReminderResponse
from app.models import User

router = APIRouter(prefix="/reminders", tags=["Recordatorios"])

@router.get("/", response_model=list[ReminderResponse])
def get_all_reminders(
    pet_id: Optional[str] = Query(None, description="Filtrar por mascota"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los recordatorios del usuario"""
    return ReminderController.get_all(db, current_user, pet_id, is_active, skip, limit)

@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder_by_id(reminder_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene un recordatorio específico"""
    return ReminderController.get_by_id(db, reminder_id, current_user)

@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(data: ReminderCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea un nuevo recordatorio"""
    return ReminderController.create(db, data, current_user)

@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: str, data: ReminderUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza un recordatorio existente"""
    return ReminderController.update(db, reminder_id, data, current_user)

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina un recordatorio"""
    ReminderController.delete(db, reminder_id, current_user)
    return None


# ========================================
# app/routes/notifications.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.notifications import NotificationController
from app.schemas.notifications import NotificationCreate, NotificationUpdate, NotificationResponse
from app.models import User

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

@router.get("/", response_model=list[NotificationResponse])
def get_all_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las notificaciones del usuario"""
    return NotificationController.get_all(db, current_user, skip, limit)

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_by_id(notification_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Obtiene una notificación específica"""
    return NotificationController.get_by_id(db, notification_id, current_user)

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(data: NotificationCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Crea una nueva notificación"""
    return NotificationController.create(db, data, current_user)

@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: str, data: NotificationUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Actualiza una notificación existente"""
    return NotificationController.update(db, notification_id, data, current_user)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Elimina una notificación"""
    NotificationController.delete(db, notification_id, current_user)
    return None


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