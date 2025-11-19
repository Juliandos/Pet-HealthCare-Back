# ========================================
# app/schemas/nutrition_plans.py
# ========================================
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class NutritionPlanBase(BaseModel):
    """Schema base para planes de nutrición"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, 
                                 description="Nombre del plan de nutrición")
    description: Optional[str] = Field(None, 
                                       description="Descripción detallada del plan")
    calories_per_day: Optional[int] = Field(None, ge=0, le=10000,
                                            description="Calorías diarias recomendadas")
    
    @validator('calories_per_day')
    def validate_calories(cls, v):
        if v is not None and v < 0:
            raise ValueError('Las calorías no pueden ser negativas')
        return v

class NutritionPlanCreate(NutritionPlanBase):
    """Schema para crear un plan de nutrición"""
    pet_id: str = Field(..., description="ID de la mascota")
    name: str = Field(..., min_length=1, max_length=200,
                     description="Nombre del plan (requerido)")

class NutritionPlanUpdate(BaseModel):
    """Schema para actualizar un plan de nutrición"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    calories_per_day: Optional[int] = Field(None, ge=0, le=10000)
    
    @validator('calories_per_day')
    def validate_calories(cls, v):
        if v is not None and v < 0:
            raise ValueError('Las calorías no pueden ser negativas')
        return v

class NutritionPlanResponse(NutritionPlanBase):
    """Schema para respuesta de plan de nutrición"""
    id: str
    pet_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NutritionPlanWithMeals(NutritionPlanResponse):
    """Schema extendido con información de comidas"""
    total_meals: int = 0
    average_calories_per_meal: Optional[float] = None

class NutritionPlanSummary(BaseModel):
    """Schema resumido para listados rápidos"""
    id: str
    pet_id: str
    name: str
    calories_per_day: Optional[int]
    
    class Config:
        from_attributes = True