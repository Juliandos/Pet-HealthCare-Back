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
        """
        Obtiene todas las mascotas del usuario actual con filtros
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
            skip: Número de registros a omitir
            limit: Número máximo de registros
            species: Filtrar por especie (opcional)
        
        Returns:
            List[Pet]: Lista de mascotas
        """
        query = db.query(Pet).filter(Pet.owner_id == current_user.id)
        
        # Filtrar por especie si se proporciona
        if species:
            query = query.filter(Pet.species.ilike(f"%{species}%"))
        
        return query.order_by(desc(Pet.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pet_by_id(db: Session, pet_id: str, current_user: User) -> Pet:
        """
        Obtiene una mascota por ID (solo del usuario actual)
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            current_user: Usuario autenticado
        
        Returns:
            Pet: Mascota encontrada
        
        Raises:
            HTTPException: Si la mascota no se encuentra
        """
        pet = db.query(Pet).filter(
            Pet.id == pet_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada o no tienes permiso para acceder a ella"
            )
        
        return pet
    
    @staticmethod
    def create_pet(db: Session, pet_data: PetCreate, current_user: User) -> Pet:
        """
        Crea una nueva mascota
        
        Args:
            db: Sesión de base de datos
            pet_data: Datos de la mascota a crear
            current_user: Usuario autenticado
        
        Returns:
            Pet: Mascota creada
        """
        # Crear nueva mascota
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
            meta={
                "name": new_pet.name,
                "species": new_pet.species,
                "breed": new_pet.breed
            }
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
        """
        Actualiza una mascota existente
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            pet_data: Datos a actualizar
            current_user: Usuario autenticado
        
        Returns:
            Pet: Mascota actualizada
        
        Raises:
            HTTPException: Si la mascota no se encuentra
        """
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Actualizar solo los campos proporcionados
        update_data = pet_data.model_dump(exclude_unset=True)
        
        # Guardar campos modificados para auditoría
        modified_fields = []
        
        for field, value in update_data.items():
            if value is not None and getattr(pet, field) != value:
                modified_fields.append(field)
                setattr(pet, field, value)
        
        # Solo actualizar updated_at si hubo cambios
        if modified_fields:
            pet.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(pet)
            
            # Log de auditoría
            audit = AuditLog(
                actor_user_id=current_user.id,
                action="PET_UPDATED",
                object_type="Pet",
                object_id=pet.id,
                meta={
                    "updated_fields": modified_fields,
                    "pet_name": pet.name
                }
            )
            db.add(audit)
            db.commit()
        
        return pet
    
    @staticmethod
    def delete_pet(db: Session, pet_id: str, current_user: User) -> bool:
        """
        Elimina una mascota
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            current_user: Usuario autenticado
        
        Returns:
            bool: True si se eliminó correctamente
        
        Raises:
            HTTPException: Si la mascota no se encuentra
        
        Note:
            Esto eliminará en cascada todos los registros relacionados:
            - Vacunaciones
            - Desparasitaciones
            - Visitas veterinarias
            - Planes de nutrición
            - Comidas
            - Recordatorios
            - Fotos
        """
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Guardar información antes de eliminar para auditoría
        pet_info = {
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "age_years": pet.age_years
        }
        
        # Log de auditoría ANTES de eliminar
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_DELETED",
            object_type="Pet",
            object_id=pet.id,
            meta=pet_info
        )
        db.add(audit)
        
        # Eliminar mascota (cascade eliminará registros relacionados)
        db.delete(pet)
        db.commit()
        
        return True
    
    @staticmethod
    def get_pet_count(db: Session, current_user: User) -> int:
        """
        Obtiene el número total de mascotas del usuario
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
        
        Returns:
            int: Número de mascotas
        """
        return db.query(Pet).filter(Pet.owner_id == current_user.id).count()
    
    @staticmethod
    def get_pets_by_species(db: Session, current_user: User) -> dict:
        """
        Obtiene un conteo de mascotas agrupadas por especie
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
        
        Returns:
            dict: Diccionario con especies como keys y conteos como values
        """
        from sqlalchemy import func
        
        results = db.query(
            Pet.species,
            func.count(Pet.id).label('count')
        ).filter(
            Pet.owner_id == current_user.id
        ).group_by(
            Pet.species
        ).all()
        
        return {species: count for species, count in results}
    
    @staticmethod
    def search_pets(
        db: Session,
        current_user: User,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Pet]:
        """
        Busca mascotas por nombre, especie o raza
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
            search_term: Término de búsqueda
            skip: Número de registros a omitir
            limit: Número máximo de registros
        
        Returns:
            List[Pet]: Lista de mascotas que coinciden
        """
        from sqlalchemy import or_
        
        search_filter = f"%{search_term}%"
        
        return db.query(Pet).filter(
            Pet.owner_id == current_user.id,
            or_(
                Pet.name.ilike(search_filter),
                Pet.species.ilike(search_filter),
                Pet.breed.ilike(search_filter)
            )
        ).order_by(desc(Pet.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pets_needing_attention(db: Session, current_user: User) -> dict:
        """
        Obtiene mascotas que necesitan atención
        (vacunas vencidas, visitas pendientes, etc.)
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
        
        Returns:
            dict: Información sobre mascotas que necesitan atención
        """
        from app.models import Vaccination, Deworming
        from datetime import date, timedelta
        from sqlalchemy import and_
        
        today = date.today()
        next_week = today + timedelta(days=7)
        
        # Mascotas con vacunas vencidas
        pets_with_overdue_vaccines = db.query(Pet).join(
            Vaccination,
            and_(
                Vaccination.pet_id == Pet.id,
                Vaccination.next_due < today,
                Vaccination.next_due.isnot(None)
            )
        ).filter(
            Pet.owner_id == current_user.id
        ).distinct().all()
        
        # Mascotas con vacunas próximas (próxima semana)
        pets_with_upcoming_vaccines = db.query(Pet).join(
            Vaccination,
            and_(
                Vaccination.pet_id == Pet.id,
                Vaccination.next_due >= today,
                Vaccination.next_due <= next_week,
                Vaccination.next_due.isnot(None)
            )
        ).filter(
            Pet.owner_id == current_user.id
        ).distinct().all()
        
        # Mascotas con desparasitaciones vencidas
        pets_with_overdue_deworming = db.query(Pet).join(
            Deworming,
            and_(
                Deworming.pet_id == Pet.id,
                Deworming.next_due < today,
                Deworming.next_due.isnot(None)
            )
        ).filter(
            Pet.owner_id == current_user.id
        ).distinct().all()
        
        return {
            "overdue_vaccines": [
                {
                    "pet_id": str(pet.id),
                    "pet_name": pet.name,
                    "species": pet.species
                }
                for pet in pets_with_overdue_vaccines
            ],
            "upcoming_vaccines": [
                {
                    "pet_id": str(pet.id),
                    "pet_name": pet.name,
                    "species": pet.species
                }
                for pet in pets_with_upcoming_vaccines
            ],
            "overdue_deworming": [
                {
                    "pet_id": str(pet.id),
                    "pet_name": pet.name,
                    "species": pet.species
                }
                for pet in pets_with_overdue_deworming
            ]
        }
    
    @staticmethod
    def bulk_update_species(
        db: Session,
        current_user: User,
        old_species: str,
        new_species: str
    ) -> int:
        """
        Actualiza la especie de múltiples mascotas a la vez
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
            old_species: Especie actual
            new_species: Nueva especie
        
        Returns:
            int: Número de mascotas actualizadas
        """
        updated_count = db.query(Pet).filter(
            Pet.owner_id == current_user.id,
            Pet.species.ilike(old_species)
        ).update(
            {Pet.species: new_species},
            synchronize_session=False
        )
        
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PETS_BULK_UPDATED",
            object_type="Pet",
            object_id=None,
            meta={
                "action": "species_update",
                "old_species": old_species,
                "new_species": new_species,
                "count": updated_count
            }
        )
        db.add(audit)
        db.commit()
        
        return updated_count