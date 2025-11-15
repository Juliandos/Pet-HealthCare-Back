from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Pet, User, AuditLog
from app.schemas.pets import PetCreate, PetUpdate
from app.utils.exceptions import UserNotFoundException
from fastapi import HTTPException, status

class PetController:
    """Controlador para operaciones con mascotas"""
    
    @staticmethod
    def get_all_pets(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
        species: Optional[str] = None
    ) -> List[Pet]:
        """Obtiene todas las mascotas del usuario actual con filtros"""
        query = db.query(Pet).filter(Pet.owner_id == current_user.id)
        
        # Filtrar por especie si se proporciona
        if species:
            query = query.filter(Pet.species.ilike(f"%{species}%"))
        
        return query.order_by(desc(Pet.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pet_by_id(db: Session, pet_id: str, current_user: User) -> Pet:
        """Obtiene una mascota por ID (solo del usuario actual)"""
        pet = db.query(Pet).filter(
            Pet.id == pet_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )
        
        return pet
    
    @staticmethod
    def create_pet(db: Session, pet_data: PetCreate, current_user: User) -> Pet:
        """Crea una nueva mascota"""
        new_pet = Pet(
            owner_id=current_user.id,
            name=pet_data.name,
            species=pet_data.species,
            breed=pet_data.breed,
            birth_date=pet_data.birth_date,
            age_years=pet_data.age_years,
            weight_kg=pet_data.weight_kg,
            sex=pet_data.sex,
            photo_url=pet_data.photo_url,
            notes=pet_data.notes
        )
        
        db.add(new_pet)
        db.commit()
        db.refresh(new_pet)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_CREATED",
            object_type="Pet",
            object_id=new_pet.id,
            meta={"name": new_pet.name, "species": new_pet.species}
        )
        db.add(audit)
        db.commit()
        
        return new_pet
    
    @staticmethod
    def update_pet(
        db: Session,
        pet_id: str,
        pet_data: PetUpdate,
        current_user: User
    ) -> Pet:
        """Actualiza una mascota existente"""
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Actualizar solo los campos proporcionados
        update_data = pet_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pet, field, value)
        
        pet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(pet)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_UPDATED",
            object_type="Pet",
            object_id=pet.id,
            meta={"updated_fields": list(update_data.keys())}
        )
        db.add(audit)
        db.commit()
        
        return pet
    
    @staticmethod
    def delete_pet(db: Session, pet_id: str, current_user: User) -> bool:
        """Elimina una mascota"""
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Log de auditoría antes de eliminar
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_DELETED",
            object_type="Pet",
            object_id=pet.id,
            meta={"name": pet.name, "species": pet.species}
        )
        db.add(audit)
        
        db.delete(pet)
        db.commit()
        
        return True