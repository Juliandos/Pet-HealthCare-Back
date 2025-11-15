from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.pets import PetController
from app.schemas.pets import (
    PetCreate,
    PetUpdate,
    PetResponse,
    PetWithStats,
    PetSummary
)
from app.models import User

router = APIRouter(prefix="/pets", tags=["Mascotas"])

# ============================================
# ENDPOINTS CRUD BÁSICOS
# ============================================

@router.get("/", response_model=List[PetResponse])
def get_all_my_pets(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    species: Optional[str] = Query(None, description="Filtrar por especie"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las mascotas del usuario autenticado
    
    Permite filtrar por especie (perro, gato, ave, etc.)
    """
    pets = PetController.get_all_pets(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        species=species
    )
    
    return [
        PetResponse(
            id=str(pet.id),
            owner_id=str(pet.owner_id),
            name=pet.name,
            species=pet.species,
            breed=pet.breed,
            birth_date=pet.birth_date,
            age_years=pet.age_years,
            weight_kg=pet.weight_kg,
            sex=pet.sex,
            photo_url=pet.photo_url,
            notes=pet.notes,
            created_at=pet.created_at.isoformat(),
            updated_at=pet.updated_at.isoformat()
        )
        for pet in pets
    ]

@router.get("/summary", response_model=List[PetSummary])
def get_pets_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de todas las mascotas (solo datos básicos)
    
    Útil para listados rápidos sin toda la información
    """
    pets = PetController.get_all_pets(
        db=db,
        current_user=current_user,
        skip=0,
        limit=100
    )
    
    return [
        PetSummary(
            id=str(pet.id),
            name=pet.name,
            species=pet.species,
            breed=pet.breed,
            age_years=pet.age_years,
            photo_url=pet.photo_url
        )
        for pet in pets
    ]

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet_by_id(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una mascota específica por ID
    
    Solo puedes ver tus propias mascotas
    """
    pet = PetController.get_pet_by_id(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    return PetResponse(
        id=str(pet.id),
        owner_id=str(pet.owner_id),
        name=pet.name,
        species=pet.species,
        breed=pet.breed,
        birth_date=pet.birth_date,
        age_years=pet.age_years,
        weight_kg=pet.weight_kg,
        sex=pet.sex,
        photo_url=pet.photo_url,
        notes=pet.notes,
        created_at=pet.created_at.isoformat(),
        updated_at=pet.updated_at.isoformat()
    )

@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    pet_data: PetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva mascota
    
    **Campos requeridos:**
    - `name`: Nombre de la mascota
    - `species`: Especie (perro, gato, ave, etc.)
    
    **Campos opcionales:**
    - `breed`: Raza
    - `birth_date`: Fecha de nacimiento
    - `age_years`: Edad en años
    - `weight_kg`: Peso en kilogramos
    - `sex`: Sexo (Macho, Hembra, Otro)
    - `photo_url`: URL de la foto
    - `notes`: Notas adicionales
    """
    pet = PetController.create_pet(
        db=db,
        pet_data=pet_data,
        current_user=current_user
    )
    
    return PetResponse(
        id=str(pet.id),
        owner_id=str(pet.owner_id),
        name=pet.name,
        species=pet.species,
        breed=pet.breed,
        birth_date=pet.birth_date,
        age_years=pet.age_years,
        weight_kg=pet.weight_kg,
        sex=pet.sex,
        photo_url=pet.photo_url,
        notes=pet.notes,
        created_at=pet.created_at.isoformat(),
        updated_at=pet.updated_at.isoformat()
    )

@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: str,
    pet_data: PetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza una mascota existente
    
    Solo se actualizarán los campos proporcionados
    """
    pet = PetController.update_pet(
        db=db,
        pet_id=pet_id,
        pet_data=pet_data,
        current_user=current_user
    )
    
    return PetResponse(
        id=str(pet.id),
        owner_id=str(pet.owner_id),
        name=pet.name,
        species=pet.species,
        breed=pet.breed,
        birth_date=pet.birth_date,
        age_years=pet.age_years,
        weight_kg=pet.weight_kg,
        sex=pet.sex,
        photo_url=pet.photo_url,
        notes=pet.notes,
        created_at=pet.created_at.isoformat(),
        updated_at=pet.updated_at.isoformat()
    )

@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una mascota
    
    ⚠️ **ADVERTENCIA:** Esto también eliminará todos los registros relacionados:
    - Vacunaciones
    - Desparasitaciones
    - Visitas veterinarias
    - Planes de nutrición
    - Comidas
    - Recordatorios
    - Fotos
    """
    PetController.delete_pet(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    return None

# ============================================
# ENDPOINTS CON ESTADÍSTICAS
# ============================================

@router.get("/{pet_id}/stats", response_model=PetWithStats)
def get_pet_with_statistics(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una mascota con estadísticas completas
    
    Incluye:
    - Total de vacunaciones
    - Total de desparasitaciones
    - Total de visitas veterinarias
    - Total de comidas registradas
    - Recordatorios activos
    """
    from app.models import (
        Vaccination, Deworming, VetVisit, Meal, Reminder
    )
    
    pet = PetController.get_pet_by_id(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    # Obtener estadísticas
    total_vaccinations = db.query(Vaccination).filter(
        Vaccination.pet_id == pet.id
    ).count()
    
    total_dewormings = db.query(Deworming).filter(
        Deworming.pet_id == pet.id
    ).count()
    
    total_vet_visits = db.query(VetVisit).filter(
        VetVisit.pet_id == pet.id
    ).count()
    
    total_meals = db.query(Meal).filter(
        Meal.pet_id == pet.id
    ).count()
    
    active_reminders = db.query(Reminder).filter(
        Reminder.pet_id == pet.id,
        Reminder.is_active == True
    ).count()
    
    return PetWithStats(
        id=str(pet.id),
        owner_id=str(pet.owner_id),
        name=pet.name,
        species=pet.species,
        breed=pet.breed,
        birth_date=pet.birth_date,
        age_years=pet.age_years,
        weight_kg=pet.weight_kg,
        sex=pet.sex,
        photo_url=pet.photo_url,
        notes=pet.notes,
        created_at=pet.created_at.isoformat(),
        updated_at=pet.updated_at.isoformat(),
        total_vaccinations=total_vaccinations,
        total_dewormings=total_dewormings,
        total_vet_visits=total_vet_visits,
        total_meals=total_meals,
        active_reminders=active_reminders
    )

# ============================================
# ENDPOINTS ADICIONALES ÚTILES
# ============================================

@router.get("/search", response_model=List[PetResponse])
def search_pets(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Busca mascotas por nombre, especie o raza
    
    Ejemplo: `/pets/search?q=golden` encontrará mascotas con "golden" en nombre, especie o raza
    """
    pets = PetController.search_pets(
        db=db,
        current_user=current_user,
        search_term=q,
        skip=skip,
        limit=limit
    )
    
    return [
        PetResponse(
            id=str(pet.id),
            owner_id=str(pet.owner_id),
            name=pet.name,
            species=pet.species,
            breed=pet.breed,
            birth_date=pet.birth_date,
            age_years=pet.age_years,
            weight_kg=pet.weight_kg,
            sex=pet.sex,
            photo_url=pet.photo_url,
            notes=pet.notes,
            created_at=pet.created_at.isoformat(),
            updated_at=pet.updated_at.isoformat()
        )
        for pet in pets
    ]

@router.get("/by-species")
def get_pets_grouped_by_species(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un conteo de mascotas agrupadas por especie
    
    Retorna: `{"perro": 3, "gato": 2, "ave": 1}`
    """
    return PetController.get_pets_by_species(db, current_user)

@router.get("/needing-attention")
def get_pets_needing_attention(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene mascotas que necesitan atención médica
    
    Incluye:
    - Mascotas con vacunas vencidas
    - Mascotas con vacunas próximas (próxima semana)
    - Mascotas con desparasitaciones vencidas
    """
    return PetController.get_pets_needing_attention(db, current_user)

# ============================================
# ENDPOINTS PARA GESTIÓN DE SALUD
# ============================================

@router.get("/{pet_id}/health-summary")
def get_pet_health_summary(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen completo de salud de la mascota
    
    Incluye:
    - Última vacunación
    - Próxima vacunación pendiente
    - Última desparasitación
    - Última visita veterinaria
    - Recordatorios activos próximos
    """
    from app.models import Vaccination, Deworming, VetVisit, Reminder
    from datetime import datetime
    from sqlalchemy import desc
    
    pet = PetController.get_pet_by_id(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    # Última vacunación
    last_vaccination = db.query(Vaccination).filter(
        Vaccination.pet_id == pet.id
    ).order_by(desc(Vaccination.date_administered)).first()
    
    # Próxima vacunación pendiente
    next_vaccination = db.query(Vaccination).filter(
        Vaccination.pet_id == pet.id,
        Vaccination.next_due != None,
        Vaccination.next_due >= datetime.utcnow().date()
    ).order_by(Vaccination.next_due).first()
    
    # Última desparasitación
    last_deworming = db.query(Deworming).filter(
        Deworming.pet_id == pet.id
    ).order_by(desc(Deworming.date_administered)).first()
    
    # Última visita veterinaria
    last_vet_visit = db.query(VetVisit).filter(
        VetVisit.pet_id == pet.id
    ).order_by(desc(VetVisit.visit_date)).first()
    
    # Próximos recordatorios (próximos 7 días)
    from datetime import timedelta
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_reminders = db.query(Reminder).filter(
        Reminder.pet_id == pet.id,
        Reminder.is_active == True,
        Reminder.event_time >= datetime.utcnow(),
        Reminder.event_time <= next_week
    ).order_by(Reminder.event_time).all()
    
    return {
        "pet_id": str(pet.id),
        "pet_name": pet.name,
        "last_vaccination": {
            "vaccine_name": last_vaccination.vaccine_name if last_vaccination else None,
            "date": last_vaccination.date_administered.isoformat() if last_vaccination else None
        } if last_vaccination else None,
        "next_vaccination_due": {
            "vaccine_name": next_vaccination.vaccine_name if next_vaccination else None,
            "due_date": next_vaccination.next_due.isoformat() if next_vaccination else None
        } if next_vaccination else None,
        "last_deworming": {
            "medication": last_deworming.medication if last_deworming else None,
            "date": last_deworming.date_administered.isoformat() if last_deworming else None
        } if last_deworming else None,
        "last_vet_visit": {
            "date": last_vet_visit.visit_date.isoformat() if last_vet_visit else None,
            "reason": last_vet_visit.reason if last_vet_visit else None
        } if last_vet_visit else None,
        "upcoming_reminders": [
            {
                "id": str(reminder.id),
                "title": reminder.title,
                "event_time": reminder.event_time.isoformat()
            }
            for reminder in upcoming_reminders
        ]
    }