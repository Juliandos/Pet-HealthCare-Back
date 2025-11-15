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
