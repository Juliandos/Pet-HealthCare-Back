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

@router.post("/pets/{pet_id}/gallery", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pet_gallery_photo(
    pet_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube una foto a la galería de una mascota
    
    **Restricciones:**
    - Tamaño máximo: 5MB (configurable)
    - Formatos permitidos: jpg, jpeg, png, gif, webp
    - La imagen se optimizará automáticamente
    
    **Ejemplo de uso con curl:**
    ```bash
    curl -X POST "http://localhost:8000/images/pets/{pet_id}/gallery" \
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
        is_profile_photo=False
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error subiendo la imagen. Verifica el formato y tamaño."
        )
    
    return ImageUploadResponse(**result)

@router.get("/pets/{pet_id}/photos", response_model=List[PetPhotoListResponse])
def get_pet_photos(
    pet_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas las fotos de una mascota
    
    Retorna información de todas las fotos almacenadas en S3 para esta mascota
    """
    photos = PetController.list_pet_photos(
        db=db,
        pet_id=pet_id,
        current_user=current_user
    )
    
    return [PetPhotoListResponse(**photo) for photo in photos]

@router.delete("/pets/{pet_id}/photos", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet_photo(
    pet_id: str,
    s3_key: str = Query(..., description="Clave del archivo en S3 (ej: pets/uuid/image.jpg)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una foto específica de una mascota
    
    **Parámetros:**
    - `pet_id`: ID de la mascota
    - `s3_key`: Clave del objeto en S3 (obtenida al listar las fotos)
    
    **Ejemplo:**
    ```
    DELETE /images/pets/{pet_id}/photos?s3_key=pets/uuid/image.jpg
    ```
    """
    success = PetController.delete_pet_photo(
        db=db,
        pet_id=pet_id,
        s3_key=s3_key,
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
    
    ⚠️ **ADVERTENCIA:** Esta acción eliminará permanentemente todas las fotos
    """
    from app.services.s3_service import s3_service
    
    # Verificar que la mascota pertenece al usuario
    PetController.get_pet_by_id(db, pet_id, current_user)
    
    # Eliminar todas las fotos
    success = s3_service.delete_pet_photos(pet_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error eliminando las imágenes"
        )
    
    return None