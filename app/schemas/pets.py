from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class PetBase(BaseModel):
    """Schema base para mascota"""
    name: str = Field(..., min_length=1, max_length=100)
    species: str = Field(..., min_length=1, max_length=50, 
                         description="Especie (perro, gato, ave, etc.)")
    breed: Optional[str] = Field(None, max_length=100, 
                                  description="Raza de la mascota")
    birth_date: Optional[date] = Field(None, 
                                        description="Fecha de nacimiento")
    age_years: Optional[int] = Field(None, ge=0, le=50, 
                                      description="Edad en años")
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=999.99, 
                                          description="Peso en kilogramos")
    sex: Optional[str] = Field(None, max_length=20, 
                                description="Sexo (Macho, Hembra, Otro)")
    photo_url: Optional[str] = Field(None, 
                                      description="URL de la foto")
    notes: Optional[str] = Field(None, 
                                  description="Notas adicionales")
    
    @validator('species')
    def validate_species(cls, v):
        valid_species = ['perro', 'gato', 'ave', 'pez', 'roedor', 'reptil', 'otro']
        if v.lower() not in valid_species:
            # Permitir cualquier valor pero sugerir los válidos
            pass
        return v.capitalize()
    
    @validator('sex')
    def validate_sex(cls, v):
        if v:
            valid_sex = ['macho', 'hembra', 'otro']
            if v.lower() not in valid_sex:
                raise ValueError(f'El sexo debe ser: {", ".join(valid_sex)}')
            return v.capitalize()
        return v

class PetCreate(PetBase):
    """Schema para crear mascota"""
    pass

class PetUpdate(BaseModel):
    """Schema para actualizar mascota"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    age_years: Optional[int] = Field(None, ge=0, le=50)
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=999.99)
    sex: Optional[str] = Field(None, max_length=20)
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('species')
    def validate_species(cls, v):
        if v:
            return v.capitalize()
        return v
    
    @validator('sex')
    def validate_sex(cls, v):
        if v:
            valid_sex = ['macho', 'hembra', 'otro']
            if v.lower() not in valid_sex:
                raise ValueError(f'El sexo debe ser: {", ".join(valid_sex)}')
            return v.capitalize()
        return v

class PetResponse(PetBase):
    """Schema para respuesta de mascota"""
    id: str
    owner_id: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }

class PetWithStats(PetResponse):
    """Schema de mascota con estadísticas"""
    total_vaccinations: int = 0
    total_dewormings: int = 0
    total_vet_visits: int = 0
    total_meals: int = 0
    active_reminders: int = 0
    
class PetSummary(BaseModel):
    """Schema resumido de mascota (para listados)"""
    id: str
    name: str
    species: str
    breed: Optional[str]
    age_years: Optional[int]
    photo_url: Optional[str]
    
    class Config:
        from_attributes = True