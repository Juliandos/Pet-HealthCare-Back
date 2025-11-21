# app/controllers/pets.py
from app.utils.helpers import calculate_age_years, get_pet_profile_photo
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from app.models import Pet, User, AuditLog, PetPhoto
from app.schemas.pets import PetCreate, PetUpdate
from app.services.s3_service import s3_service
from fastapi import HTTPException, status
import mimetypes

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
        """Obtiene todas las mascotas del usuario"""
        query = db.query(Pet).filter(Pet.owner_id == current_user.id)
        
        if species:
            query = query.filter(Pet.species.ilike(f"%{species}%"))
        
        return query.order_by(desc(Pet.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pet_by_id(db: Session, pet_id: str, current_user: User) -> Pet:
        """Obtiene una mascota por ID"""
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
            **pet_data.model_dump()
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
            meta={"pet_name": new_pet.name, "species": new_pet.species}
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
        
        # Actualizar solo campos proporcionados
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
            meta={"pet_name": pet.name, "species": pet.species}
        )
        db.add(audit)
        
        db.delete(pet)
        db.commit()
        
        return True
    
    @staticmethod
    def search_pets(
        db: Session,
        current_user: User,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Pet]:
        """Busca mascotas por nombre, especie o raza"""
        search_filter = f"%{search_term}%"
        
        pets = db.query(Pet).filter(
            Pet.owner_id == current_user.id,
            or_(
                Pet.name.ilike(search_filter),
                Pet.species.ilike(search_filter),
                Pet.breed.ilike(search_filter)
            )
        ).offset(skip).limit(limit).all()
        
        return pets
    
    @staticmethod
    def get_pets_by_species(db: Session, current_user: User) -> dict:
        """Obtiene conteo de mascotas agrupadas por especie"""
        from sqlalchemy import func
        
        results = db.query(
            Pet.species,
            func.count(Pet.id).label('count')
        ).filter(
            Pet.owner_id == current_user.id
        ).group_by(Pet.species).all()
        
        return {species: count for species, count in results}
    
    @staticmethod
    def get_pets_needing_attention(db: Session, current_user: User) -> dict:
        """Obtiene mascotas que necesitan atención médica"""
        from app.models import Vaccination, Deworming
        from datetime import date, timedelta
        
        today = date.today()
        next_week = today + timedelta(days=7)
        
        # Vacunas vencidas
        overdue_vaccinations = db.query(Pet).join(Vaccination).filter(
            Pet.owner_id == current_user.id,
            Vaccination.next_due < today
        ).distinct().all()
        
        # Vacunas próximas
        upcoming_vaccinations = db.query(Pet).join(Vaccination).filter(
            Pet.owner_id == current_user.id,
            Vaccination.next_due >= today,
            Vaccination.next_due <= next_week
        ).distinct().all()
        
        # Desparasitaciones vencidas
        overdue_dewormings = db.query(Pet).join(Deworming).filter(
            Pet.owner_id == current_user.id,
            Deworming.next_due < today
        ).distinct().all()
        
        return {
            "pets_with_overdue_vaccinations": [str(pet.id) for pet in overdue_vaccinations],
            "pets_with_upcoming_vaccinations": [str(pet.id) for pet in upcoming_vaccinations],
            "pets_with_overdue_dewormings": [str(pet.id) for pet in overdue_dewormings]
        }
    
    # Métodos para gestión de fotos S3
    @staticmethod
    def upload_pet_photo(
        db: Session,
        pet_id: str,
        file_content: bytes,
        filename: str,
        current_user: User,
        is_profile_photo: bool = False
    ) -> Optional[dict]:
        """Sube una foto de mascota a S3 y guarda el registro en pet_photos"""
        # Verificar que la mascota pertenece al usuario
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Subir a S3
        if is_profile_photo:
            result = s3_service.upload_pet_profile_photo(
                file_content=file_content,
                filename=filename,
                pet_id=pet_id
            )
        else:
            result = s3_service.upload_pet_gallery_photo(
                file_content=file_content,
                filename=filename,
                pet_id=pet_id
            )
        
        if not result:
            return None
        
        # Determinar tipo MIME
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            # Fallback basado en extensión
            extension = filename.lower().split('.')[-1]
            mime_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            mime_type = mime_type_map.get(extension, 'image/jpeg')
        
        # Crear registro en la tabla pet_photos
        pet_photo = PetPhoto(
            pet_id=pet.id,
            file_name=filename,
            file_size_bytes=result['size'],
            mime_type=mime_type,
            url=result['url'],
            data=None  # No guardamos los bytes en BD, están en S3
        )
        db.add(pet_photo)
        db.commit()
        db.refresh(pet_photo)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_PHOTO_UPLOADED",
            object_type="Pet",
            object_id=pet.id,
            meta={
                "photo_id": str(pet_photo.id),
                "s3_key": result['key'],
                "size": result['size'],
                "is_profile": is_profile_photo
            }
        )
        db.add(audit)
        db.commit()
        
        # Retornar información incluyendo el ID del registro
        return {
            **result,
            "photo_id": str(pet_photo.id)
        }
    
    @staticmethod
    def delete_pet_photo(
        db: Session,
        pet_id: str,
        photo_id: str,
        current_user: User
    ) -> bool:
        """Elimina una foto de mascota de S3 y de la base de datos"""
        # Verificar que la mascota pertenece al usuario
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Buscar el registro en pet_photos
        pet_photo = db.query(PetPhoto).filter(
            PetPhoto.id == photo_id,
            PetPhoto.pet_id == pet.id
        ).first()
        
        if not pet_photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto no encontrada"
            )
        
        # Extraer s3_key de la URL o usar el campo url
        s3_key = None
        if pet_photo.url:
            # Extraer la clave S3 de la URL
            # Formato: https://bucket.s3.region.amazonaws.com/pets/{pet_id}/filename.jpg
            url_parts = pet_photo.url.split('.amazonaws.com/')
            if len(url_parts) > 1:
                s3_key = url_parts[1]
        
        # Eliminar de S3 si tenemos la clave
        s3_success = True
        if s3_key:
            s3_success = s3_service.delete_image(s3_key)
        
        # Eliminar registro de la base de datos
        db.delete(pet_photo)
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_PHOTO_DELETED",
            object_type="Pet",
            object_id=pet.id,
            meta={
                "photo_id": str(photo_id),
                "s3_key": s3_key or "unknown"
            }
        )
        db.add(audit)
        db.commit()
        
        return s3_success
    
    @staticmethod
    def list_pet_photos(
        db: Session,
        pet_id: str,
        current_user: User
    ) -> list[dict]:
        """Lista todas las fotos de una mascota desde la tabla pet_photos"""
        # Verificar que la mascota pertenece al usuario
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Listar fotos desde la base de datos
        pet_photos = db.query(PetPhoto).filter(
            PetPhoto.pet_id == pet.id
        ).order_by(desc(PetPhoto.created_at)).all()
        
        # Convertir a formato de respuesta
        photos_list = []
        for photo in pet_photos:
            # Extraer s3_key de la URL para compatibilidad
            s3_key = None
            if photo.url:
                url_parts = photo.url.split('.amazonaws.com/')
                if len(url_parts) > 1:
                    s3_key = url_parts[1]
            
            photos_list.append({
                "id": str(photo.id),
                "pet_id": str(photo.pet_id),
                "file_name": photo.file_name,
                "file_size_bytes": photo.file_size_bytes,
                "mime_type": photo.mime_type,
                "url": photo.url,
                "key": s3_key or photo.url,  # Para compatibilidad con esquema actual
                "size": photo.file_size_bytes or 0,
                "last_modified": photo.updated_at.isoformat() if photo.updated_at else photo.created_at.isoformat(),
                "created_at": photo.created_at.isoformat()
            })
        
        return photos_list