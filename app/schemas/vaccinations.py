# ========================================
# app/schemas/vaccinations.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class VaccinationBase(BaseModel):
    vaccine_name: str = Field(..., min_length=1, max_length=200)
    manufacturer: Optional[str] = Field(None, max_length=200)
    lot_number: Optional[str] = Field(None, max_length=100)
    date_administered: date
    next_due: Optional[date] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    proof_document_id: Optional[str] = None

class VaccinationCreate(VaccinationBase):
    pet_id: str

class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = Field(None, min_length=1, max_length=200)
    manufacturer: Optional[str] = Field(None, max_length=200)
    lot_number: Optional[str] = Field(None, max_length=100)
    date_administered: Optional[date] = None
    next_due: Optional[date] = None
    veterinarian: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    proof_document_id: Optional[str] = None

class VaccinationResponse(VaccinationBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None
        }

# ========================================
# app/schemas/nutrition_plans.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NutritionPlanBase(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    calories_per_day: Optional[int] = Field(None, ge=0)

class NutritionPlanCreate(NutritionPlanBase):
    pet_id: str

class NutritionPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    calories_per_day: Optional[int] = Field(None, ge=0)

class NutritionPlanResponse(NutritionPlanBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========================================
# app/schemas/meals.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MealBase(BaseModel):
    meal_time: datetime
    description: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    plan_id: Optional[str] = None

class MealCreate(MealBase):
    pet_id: str

class MealUpdate(BaseModel):
    meal_time: Optional[datetime] = None
    description: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    plan_id: Optional[str] = None

class MealResponse(MealBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========================================
# app/schemas/reminders.py
# ========================================
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models import ReminderFrequency

class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_time: datetime
    timezone: Optional[str] = "UTC"
    frequency: ReminderFrequency = ReminderFrequency.once
    rrule: Optional[str] = None
    is_active: bool = True
    notify_by_email: bool = True
    notify_in_app: bool = True
    pet_id: Optional[str] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_time: Optional[datetime] = None
    timezone: Optional[str] = None
    frequency: Optional[ReminderFrequency] = None
    rrule: Optional[str] = None
    is_active: Optional[bool] = None
    notify_by_email: Optional[bool] = None
    notify_in_app: Optional[bool] = None
    pet_id: Optional[str] = None

class ReminderResponse(ReminderBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ReminderFrequency: lambda v: v.value
        }


# ========================================
# app/schemas/notifications.py
# ========================================
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class NotificationBase(BaseModel):
    reminder_id: Optional[str] = None
    pet_id: Optional[str] = None
    sent_at: datetime
    method: Optional[str] = None
    status: Optional[str] = None
    provider_response: Optional[Any] = None

class NotificationCreate(NotificationBase):
    owner_id: str

class NotificationUpdate(BaseModel):
    method: Optional[str] = None
    status: Optional[str] = None
    provider_response: Optional[Any] = None

class NotificationResponse(NotificationBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========================================
# app/schemas/pet_photos.py
# ========================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PetPhotoBase(BaseModel):
    file_name: Optional[str] = Field(None, max_length=500)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = None

class PetPhotoCreate(PetPhotoBase):
    pet_id: str
    data: Optional[bytes] = None  # Para subir archivo directamente

class PetPhotoUpdate(BaseModel):
    file_name: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = None

class PetPhotoResponse(PetPhotoBase):
    id: str
    pet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }