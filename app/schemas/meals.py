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


