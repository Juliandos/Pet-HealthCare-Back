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


# ========================================
# app/controllers/reminders.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Reminder, Pet, User, AuditLog
from app.schemas.reminders import ReminderCreate, ReminderUpdate
from fastapi import HTTPException, status

class ReminderController:
    @staticmethod
    def get_all(db: Session, current_user: User, pet_id: Optional[str] = None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Reminder]:
        query = db.query(Reminder).filter(Reminder.owner_id == current_user.id)
        if pet_id:
            query = query.filter(Reminder.pet_id == pet_id)
        if is_active is not None:
            query = query.filter(Reminder.is_active == is_active)
        return query.order_by(Reminder.event_time).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, reminder_id: str, current_user: User) -> Reminder:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.owner_id == current_user.id).first()
        if not reminder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recordatorio no encontrado")
        return reminder
    
    @staticmethod
    def create(db: Session, data: ReminderCreate, current_user: User) -> Reminder:
        if data.pet_id:
            pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == current_user.id).first()
            if not pet:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        
        new_item = Reminder(owner_id=current_user.id, **data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        audit = AuditLog(actor_user_id=current_user.id, action="REMINDER_CREATED", object_type="Reminder", object_id=new_item.id)
        db.add(audit)
        db.commit()
        return new_item
    
    @staticmethod
    def update(db: Session, reminder_id: str, data: ReminderUpdate, current_user: User) -> Reminder:
        reminder = ReminderController.get_by_id(db, reminder_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)
        reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        
        audit = AuditLog(actor_user_id=current_user.id, action="REMINDER_UPDATED", object_type="Reminder", object_id=reminder.id)
        db.add(audit)
        db.commit()
        return reminder
    
    @staticmethod
    def delete(db: Session, reminder_id: str, current_user: User) -> bool:
        reminder = ReminderController.get_by_id(db, reminder_id, current_user)
        audit = AuditLog(actor_user_id=current_user.id, action="REMINDER_DELETED", object_type="Reminder", object_id=reminder.id)
        db.add(audit)
        db.delete(reminder)
        db.commit()
        return True


# ========================================
# app/controllers/notifications.py
# ========================================
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Notification, User, AuditLog
from app.schemas.notifications import NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status

class NotificationController:
    @staticmethod
    def get_all(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[Notification]:
        return db.query(Notification).filter(Notification.owner_id == current_user.id).order_by(desc(Notification.sent_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, notification_id: str, current_user: User) -> Notification:
        notif = db.query(Notification).filter(Notification.id == notification_id, Notification.owner_id == current_user.id).first()
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        return notif
    
    @staticmethod
    def create(db: Session, data: NotificationCreate, current_user: User) -> Notification:
        new_item = Notification(**data.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    
    @staticmethod
    def update(db: Session, notification_id: str, data: NotificationUpdate, current_user: User) -> Notification:
        notif = NotificationController.get_by_id(db, notification_id, current_user)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notif, field, value)
        notif.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(notif)
        return notif
    
    @staticmethod
    def delete(db: Session, notification_id: str, current_user: User) -> bool:
        notif = NotificationController.get_by_id(db, notification_id, current_user)
        db.delete(notif)
        db.commit()
        return True


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