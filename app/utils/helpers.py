from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc


def calculate_age_years(birth_date: Optional[date]) -> Optional[int]:
    """
    Calcula la edad en años basado en la fecha de nacimiento
    
    Args:
        birth_date: Fecha de nacimiento
    
    Returns:
        Edad en años o None si no hay birth_date
    
    Example:
        >>> from datetime import date
        >>> birth_date = date(2020, 5, 15)
        >>> age = calculate_age_years(birth_date)
        >>> age
        4  # (en 2024)
    """
    if not birth_date:
        return None
    
    today = date.today()
    age = today.year - birth_date.year
    
    # Ajustar si el cumpleaños aún no ha pasado este año
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


def get_pet_profile_photo(db: Session, pet_id: str) -> Optional[str]:
    """
    Obtiene la URL de la foto de perfil de una mascota
    
    Busca específicamente la foto marcada como is_profile=True.
    Si no hay foto de perfil, retorna None.
    
    Args:
        db: Sesión de base de datos
        pet_id: ID de la mascota
    
    Returns:
        URL de la foto de perfil o None si no hay foto de perfil
    
    Example:
        >>> photo_url = get_pet_profile_photo(db, "pet-uuid")
        >>> photo_url
        'https://s3.amazonaws.com/pets/uuid/image.jpg'
    """
    from app.models import PetPhoto
    
    try:
        pet_photo = db.query(PetPhoto)\
            .filter(
                PetPhoto.pet_id == pet_id,
                PetPhoto.is_profile == True  # ✅ Solo fotos de perfil
            )\
            .order_by(desc(PetPhoto.created_at))\
            .first()
        
        return pet_photo.url if pet_photo else None
    except Exception as e:
        print(f"❌ Error obteniendo foto de perfil: {str(e)}")
        return None