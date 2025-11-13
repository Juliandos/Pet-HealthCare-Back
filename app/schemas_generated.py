import uuid
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field
from app.models import ReminderFrequency

# Base Schema for common fields
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseSchema):
    username: Optional[str] = None
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    role: Optional[str] = "user"
    auth_provider: Optional[str] = "local"
    email_verified: Optional[bool] = False
    failed_attempts: Optional[int] = 0
    locked_until: Optional[datetime] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None # Email can be updated
    password: Optional[str] = None
    role: Optional[str] = None
    auth_provider: Optional[str] = None
    email_verified: Optional[bool] = None
    failed_attempts: Optional[int] = None
    locked_until: Optional[datetime] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: uuid.UUID
    verification_token: Optional[str] = None # Should not be exposed in read
    refresh_token: Optional[str] = None # Should not be exposed in read
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Relationships - forward references
    pets: List["PetRead"] = []
    reminders: List["ReminderRead"] = []
    notifications: List["NotificationRead"] = []
    password_resets: List["PasswordResetRead"] = []
    audit_logs: List["AuditLogRead"] = []

# Pet Schemas
class PetBase(BaseSchema):
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    age_years: Optional[int] = None
    weight_kg: Optional[float] = None
    sex: Optional[str] = None
    photo_url: Optional[str] = None
    photo_bytea: Optional[bytes] = None
    notes: Optional[str] = None

class PetCreate(PetBase):
    owner_id: uuid.UUID

class PetUpdate(PetBase):
    name: Optional[str] = None
    species: Optional[str] = None

class PetRead(PetBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    owner: Optional[UserRead] = None
    photos: List["PetPhotoRead"] = []
    vaccinations: List["VaccinationRead"] = []
    dewormings: List["DewormingRead"] = []
    vet_visits: List["VetVisitRead"] = []
    nutrition_plans: List["NutritionPlanRead"] = []
    meals: List["MealRead"] = []
    reminders: List["ReminderRead"] = []
    notifications: List["NotificationRead"] = []

# PetPhoto Schemas
class PetPhotoBase(BaseSchema):
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    url: Optional[str] = None
    data: Optional[bytes] = None

class PetPhotoCreate(PetPhotoBase):
    pet_id: uuid.UUID

class PetPhotoUpdate(PetPhotoBase):
    pass

class PetPhotoRead(PetPhotoBase):
    id: uuid.UUID
    pet_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    pet: Optional[PetRead] = None

# Vaccination Schemas
class VaccinationBase(BaseSchema):
    vaccine_name: str
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    date_administered: date
    next_due: Optional[date] = None
    veterinarian: Optional[str] = None
    notes: Optional[str] = None
    proof_document_id: Optional[uuid.UUID] = None

class VaccinationCreate(VaccinationBase):
    pet_id: uuid.UUID

class VaccinationUpdate(VaccinationBase):
    vaccine_name: Optional[str] = None
    date_administered: Optional[date] = None

class VaccinationRead(VaccinationBase):
    id: uuid.UUID
    pet_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    pet: Optional[PetRead] = None
    proof_document: Optional[PetPhotoRead] = None

# Deworming Schemas
class DewormingBase(BaseSchema):
    medication: Optional[str] = None
    date_administered: date
    next_due: Optional[date] = None
    veterinarian: Optional[str] = None
    notes: Optional[str] = None

class DewormingCreate(DewormingBase):
    pet_id: uuid.UUID

class DewormingUpdate(DewormingBase):
    date_administered: Optional[date] = None

class DewormingRead(DewormingBase):
    id: uuid.UUID
    pet_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    pet: Optional[PetRead] = None

# VetVisit Schemas
class VetVisitBase(BaseSchema):
    visit_date: datetime
    reason: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    veterinarian: Optional[str] = None
    documents_id: Optional[uuid.UUID] = None

class VetVisitCreate(VetVisitBase):
    pet_id: uuid.UUID

class VetVisitUpdate(VetVisitBase):
    visit_date: Optional[datetime] = None

class VetVisitRead(VetVisitBase):
    id: uuid.UUID
    pet_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    pet: Optional[PetRead] = None
    documents: Optional[PetPhotoRead] = None

# NutritionPlan Schemas
class NutritionPlanBase(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    calories_per_day: Optional[int] = None

class NutritionPlanCreate(NutritionPlanBase):
    pet_id: uuid.UUID

class NutritionPlanUpdate(NutritionPlanBase):
    pass

class NutritionPlanRead(NutritionPlanBase):
    id: uuid.UUID
    pet_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    pet: Optional[PetRead] = None
    meals: List["MealRead"] = []

# Meal Schemas
class MealBase(BaseSchema):
    plan_id: Optional[uuid.UUID] = None
    meal_time: datetime
    description: Optional[str] = None
    calories: Optional[int] = None

class MealCreate(MealBase):
    pet_id: uuid.UUID

class MealUpdate(MealBase):
    meal_time: Optional[datetime] = None

class MealRead(MealBase):
    id: uuid.UUID
    pet_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    pet: Optional[PetRead] = None
    nutrition_plan: Optional[NutritionPlanRead] = None

# Reminder Schemas
class ReminderBase(BaseSchema):
    title: str
    description: Optional[str] = None
    event_time: datetime
    timezone: Optional[str] = None
    frequency: Optional[ReminderFrequency] = ReminderFrequency.once
    rrule: Optional[str] = None
    is_active: Optional[bool] = True
    notify_by_email: Optional[bool] = True
    notify_in_app: Optional[bool] = True

class ReminderCreate(ReminderBase):
    owner_id: uuid.UUID
    pet_id: Optional[uuid.UUID] = None

class ReminderUpdate(ReminderBase):
    title: Optional[str] = None
    event_time: Optional[datetime] = None

class ReminderRead(ReminderBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    pet_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    owner: Optional[UserRead] = None
    pet: Optional[PetRead] = None
    notifications: List["NotificationRead"] = []

# Notification Schemas
class NotificationBase(BaseSchema):
    reminder_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None
    pet_id: Optional[uuid.UUID] = None
    sent_at: datetime
    method: Optional[str] = None
    status: Optional[str] = None
    provider_response: Optional[Any] = None # JSONB can be any type

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    sent_at: Optional[datetime] = None

class NotificationRead(NotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    reminder: Optional[ReminderRead] = None
    owner: Optional[UserRead] = None
    pet: Optional[PetRead] = None

# PasswordReset Schemas
class PasswordResetBase(BaseSchema):
    token: str
    expires_at: datetime
    used: Optional[bool] = False

class PasswordResetCreate(PasswordResetBase):
    user_id: uuid.UUID

class PasswordResetUpdate(PasswordResetBase):
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    used: Optional[bool] = None

class PasswordResetRead(PasswordResetBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    user: Optional[UserRead] = None

# AuditLog Schemas
class AuditLogBase(BaseSchema):
    actor_user_id: Optional[uuid.UUID] = None
    action: str
    object_type: Optional[str] = None
    object_id: Optional[uuid.UUID] = None
    meta: Optional[Any] = None # JSONB can be any type

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogUpdate(AuditLogBase):
    action: Optional[str] = None

class AuditLogRead(AuditLogBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    actor: Optional[UserRead] = None

# Update forward refs for relationships
UserRead.model_rebuild()
PetRead.model_rebuild()
PetPhotoRead.model_rebuild()
VaccinationRead.model_rebuild()
DewormingRead.model_rebuild()
VetVisitRead.model_rebuild()
NutritionPlanRead.model_rebuild()
MealRead.model_rebuild()
ReminderRead.model_rebuild()
NotificationRead.model_rebuild()
PasswordResetRead.model_rebuild()
AuditLogRead.model_rebuild()
