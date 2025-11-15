from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Vaccination, Pet, User, AuditLog
from app.schemas.vaccinations import VaccinationCreate, VaccinationUpdate
from fastapi import HTTPException, status

class VaccinationController:
    """Controlador para operaciones con vacunaciones"""
    
    @staticmethod
    def get_all_vaccinations(
        db: Session,
        current_user: User,
        pet_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vaccination]:
        """Obtiene todas las vacunaciones del usuario (opcionalmente filtradas por mascota)"""
        # Base query - solo vacunas de mascotas del usuario
        query = db.query(Vaccination).join(Pet).filter(Pet.owner_id == current_user.id)
        
        # Filtrar por mascota específica si se proporciona
        if pet_id:
            query = query.filter(Vaccination.pet_id == pet_id)
        
        return query.order_by(desc(Vaccination.date_administered)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_vaccination_by_id(db: Session, vaccination_id: str, current_user: User) -> Vaccination:
        """Obtiene una vacunación por ID (solo del usuario actual)"""
        vaccination = db.query(Vaccination).join(Pet).filter(
            Vaccination.id == vaccination_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not vaccination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vacunación no encontrada"
            )
        
        return vaccination
    
    @staticmethod
    def create_vaccination(
        db: Session,
        vaccination_data: VaccinationCreate,
        current_user: User
    ) -> Vaccination:
        """Crea una nueva vacunación"""
        # Verificar que la mascota pertenece al usuario
        pet = db.query(Pet).filter(
            Pet.id == vaccination_data.pet_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )
        
        new_vaccination = Vaccination(
            pet_id=vaccination_data.pet_id,
            vaccine_name=vaccination_data.vaccine_name,
            manufacturer=vaccination_data.manufacturer,
            lot_number=vaccination_data.lot_number,
            date_administered=vaccination_data.date_administered,
            next_due=vaccination_data.next_due,
            veterinarian=vaccination_data.veterinarian,
            notes=vaccination_data.notes,
            proof_document_id=vaccination_data.proof_document_id
        )
        
        db.add(new_vaccination)
        db.commit()
        db.refresh(new_vaccination)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="VACCINATION_CREATED",
            object_type="Vaccination",
            object_id=new_vaccination.id,
            meta={
                "pet_id": str(vaccination_data.pet_id),
                "vaccine_name": vaccination_data.vaccine_name
            }
        )
        db.add(audit)
        db.commit()
        
        return new_vaccination
    
    @staticmethod
    def update_vaccination(
        db: Session,
        vaccination_id: str,
        vaccination_data: VaccinationUpdate,
        current_user: User
    ) -> Vaccination:
        """Actualiza una vacunación existente"""
        vaccination = VaccinationController.get_vaccination_by_id(db, vaccination_id, current_user)
        
        # Actualizar solo los campos proporcionados
        update_data = vaccination_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vaccination, field, value)
        
        vaccination.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vaccination)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="VACCINATION_UPDATED",
            object_type="Vaccination",
            object_id=vaccination.id,
            meta={"updated_fields": list(update_data.keys())}
        )
        db.add(audit)
        db.commit()
        
        return vaccination
    
    @staticmethod
    def delete_vaccination(db: Session, vaccination_id: str, current_user: User) -> bool:
        """Elimina una vacunación"""
        vaccination = VaccinationController.get_vaccination_by_id(db, vaccination_id, current_user)
        
        # Log de auditoría antes de eliminar
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="VACCINATION_DELETED",
            object_type="Vaccination",
            object_id=vaccination.id,
            meta={
                "pet_id": str(vaccination.pet_id),
                "vaccine_name": vaccination.vaccine_name
            }
        )
        db.add(audit)
        
        db.delete(vaccination)
        db.commit()
        
        return True