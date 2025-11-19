# Agregar estas funciones al final del archivo app/controllers/pets.py

from app.services.s3_service import s3_service

class PetController:
    # ... métodos existentes ...
    
    @staticmethod
    def upload_pet_photo(
        db: Session,
        pet_id: str,
        file_content: bytes,
        filename: str,
        current_user: User,
        is_profile_photo: bool = False
    ) -> Optional[dict]:
        """
        Sube una foto de mascota a S3
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            file_content: Contenido binario del archivo
            filename: Nombre del archivo
            current_user: Usuario autenticado
            is_profile_photo: Si es foto de perfil
        
        Returns:
            Información de la foto subida
        """
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
        
        # Si es foto de perfil, actualizar la mascota
        if is_profile_photo:
            pet.photo_url = result['url']
            db.commit()
            db.refresh(pet)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PET_PHOTO_UPLOADED",
            object_type="Pet",
            object_id=pet.id,
            meta={
                "s3_key": result['key'],
                "size": result['size'],
                "is_profile": is_profile_photo
            }
        )
        db.add(audit)
        db.commit()
        
        return result
    
    @staticmethod
    def delete_pet_photo(
        db: Session,
        pet_id: str,
        s3_key: str,
        current_user: User
    ) -> bool:
        """
        Elimina una foto de mascota de S3
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            s3_key: Clave del objeto en S3
            current_user: Usuario autenticado
        
        Returns:
            True si se eliminó correctamente
        """
        # Verificar que la mascota pertenece al usuario
        pet = PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Eliminar de S3
        success = s3_service.delete_image(s3_key)
        
        if success:
            # Si era la foto de perfil, limpiar la URL
            if pet.photo_url and s3_key in pet.photo_url:
                pet.photo_url = None
                db.commit()
            
            # Log de auditoría
            audit = AuditLog(
                actor_user_id=current_user.id,
                action="PET_PHOTO_DELETED",
                object_type="Pet",
                object_id=pet.id,
                meta={"s3_key": s3_key}
            )
            db.add(audit)
            db.commit()
        
        return success
    
    @staticmethod
    def list_pet_photos(
        db: Session,
        pet_id: str,
        current_user: User
    ) -> list[dict]:
        """
        Lista todas las fotos de una mascota
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            current_user: Usuario autenticado
        
        Returns:
            Lista de fotos
        """
        # Verificar que la mascota pertenece al usuario
        PetController.get_pet_by_id(db, pet_id, current_user)
        
        # Listar fotos de S3
        return s3_service.list_pet_photos(pet_id)