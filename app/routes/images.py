# ========================================
# app/routes/images.py
# ========================================
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.pets import PetController
from app.schemas.images import ImageUploadResponse, PetPhotoListResponse
from app.models import User

router = APIRouter(prefix="/images", tags=["Imágenes"])

@router.post("/pets/{pet_id}/profile", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pet_profile_photo(
    pet_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube o actualiza la foto de perfil de una mascota
    
    **Restricciones:**
    - Tamaño máximo: 5MB (configurable)
    - Formatos permitidos: jpg, jpeg, png, gif, webp
    - La imagen se optimizará automáticamente
    - **Solo puede haber 1 foto de perfil por mascota** (se reemplaza la anterior)
    - **Límite total: 6 fotos (5 galería + 1 perfil)**
    
    **Ejemplo de uso con curl:**
    ```bash
    curl -X POST "http://localhost:8000/images/pets/{pet_id}/profile" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -F "file=@/path/to/image.jpg"
    ```
    """
    # Leer contenido del archivo
    file_content = await file.read()
    
    # Subir imagen
    result = PetController.upload_pet_photo(
        db=db,
        pet_id=pet_id,
        file_content=file_content,
        filename=file.filename,
        current_user=current_user,
        is_profile_photo=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error subiendo la imagen. Verifica el formato y tamaño."
        )
    
    return ImageUploadResponse(**result)

@router.post("/pets/{pet_id}/gallery", response_model=List[ImageUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_pet_gallery_photo(
    pet_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube una o múltiples fotos a la galería de una mascota (máximo 5 imágenes)
    
    **Restricciones:**
    - Tamaño máximo por imagen: 5MB (configurable)
    - Formatos permitidos: jpg, jpeg, png, gif, webp
    - Las imágenes se optimizarán automáticamente
    - **Máximo 5 imágenes por petición**
    - **Límite máximo: 5 fotos de galería por mascota**
    - **Límite total: 6 fotos (5 galería + 1 perfil)**
    
    **Ejemplo de uso con curl (una imagen):**
    ```bash
    curl -X POST "http://localhost:8000/images/pets/{pet_id}/gallery" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -F "files=@/path/to/image.jpg"
    ```
    
    **Ejemplo de uso con curl (múltiples imágenes, hasta 5):**
    ```bash
    curl -X POST "http://localhost:8000/images/pets/{pet_id}/gallery" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -F "files=@/path/to/image1.jpg" \
      -F "files=@/path/to/image2.jpg" \
      -F "files=@/path/to/image3.jpg"
    ```
    
    **Nota:** En el frontend, puedes usar un input file con `multiple`:
    ```html
    <input type="file" name="files" multiple accept="image/*" />
    ```
    """
    # Validar que no se suban más de 5 archivos
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Se pueden subir máximo 5 imágenes a la vez. Se intentaron subir {len(files)} imágenes."
        )
    
    # Validar que se haya enviado al menos un archivo
    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos una imagen"
        )
    
    results = []
    errors = []
    
    # Procesar cada archivo
    for index, file in enumerate(files):
        try:
            # Leer contenido del archivo
            file_content = await file.read()
            
            # Validar que el archivo no esté vacío
            if len(file_content) == 0:
                errors.append(f"Imagen {index + 1} ({file.filename}): El archivo está vacío")
                continue
            
            # Subir imagen
            result = PetController.upload_pet_photo(
                db=db,
                pet_id=pet_id,
                file_content=file_content,
                filename=file.filename or f"image_{index + 1}.jpg",
                current_user=current_user,
                is_profile_photo=False
            )
            
            if result:
                results.append(ImageUploadResponse(**result))
            else:
                errors.append(f"Imagen {index + 1} ({file.filename}): Error subiendo la imagen")
                
        except HTTPException as e:
            # Capturar errores de validación del controlador (límites, formato, etc.)
            errors.append(f"Imagen {index + 1} ({file.filename}): {e.detail}")
        except Exception as e:
            # Capturar otros errores inesperados
            errors.append(f"Imagen {index + 1} ({file.filename}): {str(e)}")
    
    # Si no se subió ninguna imagen, retornar error
    if len(results) == 0:
        error_message = "No se pudo subir ninguna imagen. Errores:\n" + "\n".join(errors)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Si algunas imágenes fallaron pero otras se subieron correctamente
    if len(errors) > 0:
        # Retornar las exitosas pero incluir advertencia en la respuesta
        # (FastAPI no permite modificar headers fácilmente, así que incluimos en el body)
        # Por ahora, retornamos solo las exitosas
        pass
    
    return results

@router.get("/pets/{pet_id}/photos", response_model=List[PetPhotoListResponse])
def get_pet_photos(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas las fotos de una mascota
    
    Retorna información de todas las fotos almacenadas en la tabla pet_photos.
    Las imágenes físicas están en S3, pero los metadatos se leen desde la base de datos.
    """
    photos = PetController.list_pet_photos(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    return [PetPhotoListResponse(**photo) for photo in photos]

@router.delete("/pets/{pet_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet_photo(
    pet_id: str,
    photo_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una foto específica de una mascota
    
    **Parámetros:**
    - `pet_id`: ID de la mascota
    - `photo_id`: ID del registro en pet_photos (obtenido al listar las fotos)
    
    **Ejemplo:**
    ```
    DELETE /images/pets/{pet_id}/photos/{photo_id}
    ```
    """
    success = PetController.delete_pet_photo(
        db=db,
        pet_id=pet_id,
        photo_id=photo_id,
        current_user=current_user
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error eliminando la imagen"
        )
    
    return None

@router.delete("/pets/{pet_id}/photos/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_pet_photos(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina todas las fotos de una mascota
    
    ⚠️ **ADVERTENCIA:** Esta acción eliminará permanentemente todas las fotos de S3 y de la base de datos
    """
    from app.services.s3_service import s3_service
    from app.models import PetPhoto
    
    # Verificar que la mascota pertenece al usuario
    pet = PetController.get_pet_by_id(db, pet_id, current_user)
    
    # Obtener todas las fotos de la base de datos
    pet_photos = db.query(PetPhoto).filter(PetPhoto.pet_id == pet.id).all()
    
    # Eliminar de S3 y de la BD
    deleted_count = 0
    for photo in pet_photos:
        # Extraer s3_key de la URL
        s3_key = None
        if photo.url:
            url_parts = photo.url.split('.amazonaws.com/')
            if len(url_parts) > 1:
                s3_key = url_parts[1]
                s3_service.delete_image(s3_key)
        
        # Eliminar registro de la BD
        db.delete(photo)
        deleted_count += 1
    
    db.commit()
    
    return None