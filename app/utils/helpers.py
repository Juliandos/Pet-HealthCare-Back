from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from dateutil.relativedelta import relativedelta


def calculate_age_years(birth_date: Optional[date]) -> Optional[float]:
    """
    Calcula la edad en años con decimales basado en la fecha de nacimiento
    Incluye meses como fracción de año (ej: 1 año y 6 meses = 1.5 años)
    
    Args:
        birth_date: Fecha de nacimiento
    
    Returns:
        Edad en años con decimales o None si no hay birth_date
    
    Examples:
        >>> from datetime import date
        >>> birth_date = date(2023, 1, 15)  # 15 enero 2023
        >>> today = date(2024, 7, 15)  # 15 julio 2024
        >>> age = calculate_age_years(birth_date)
        >>> age
        1.5  # 1 año y 6 meses
        
        >>> birth_date = date(2023, 12, 1)  # 1 diciembre 2023
        >>> today = date(2024, 1, 1)  # 1 enero 2024
        >>> age = calculate_age_years(birth_date)
        >>> age
        0.083333  # 1 mes (1/12 = 0.083333)
        
        >>> birth_date = date(2023, 10, 1)  # 1 octubre 2023
        >>> today = date(2024, 1, 1)  # 1 enero 2024
        >>> age = calculate_age_years(birth_date)
        >>> age
        0.25  # 3 meses (3/12 = 0.25)
    """
    if not birth_date:
        return None
    
    today = date.today()
    
    # Usar relativedelta para calcular diferencia exacta en años y meses
    delta = relativedelta(today, birth_date)
    
    # Obtener años y meses
    years = delta.years
    months = delta.months
    
    # Si el día actual es menor que el día de nacimiento,
    # aún no ha cumplido el mes completo, así que no contamos ese mes
    if today.day < birth_date.day:
        months -= 1
        # Si meses es negativo, ajustar
        if months < 0:
            months = 11
            years -= 1
    
    # Asegurar que meses esté en rango 0-11
    if months < 0:
        months = 0
    elif months > 11:
        # Esto no debería pasar con relativedelta, pero por seguridad
        extra_years = months // 12
        years += extra_years
        months = months % 12
    
    # Convertir meses a fracción de año
    months_fraction = months / 12.0
    
    # Calcular edad total en años con decimales
    age = years + months_fraction
    
    # Redondear a 6 decimales para precisión
    return round(age, 6)


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