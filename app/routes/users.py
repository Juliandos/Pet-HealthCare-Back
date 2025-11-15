from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.middleware.auth import (
    get_db, 
    get_current_active_user,
    require_role
)
from app.controllers.users import UserController
from app.schemas.users import (
    UserUpdate,
    UserChangePassword,
    UserResponse,
    UserStatistics
)
from app.models import User

router = APIRouter(prefix="/users", tags=["Usuarios"])

# ============================================
# ENDPOINTS PÚBLICOS (requieren autenticación básica)
# ============================================

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene el perfil del usuario autenticado actual
    """
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        timezone=current_user.timezone,
        role=current_user.role,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat()
    )

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado
    
    **Nota:** Los usuarios normales no pueden cambiar `role`, `email_verified` ni `is_active`
    """
    updated_user = UserController.update_user(
        db=db,
        user_id=str(current_user.id),
        user_data=user_data,
        current_user=current_user
    )
    
    return UserResponse(
        id=str(updated_user.id),
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        phone=updated_user.phone,
        timezone=updated_user.timezone,
        role=updated_user.role,
        email_verified=updated_user.email_verified,
        is_active=updated_user.is_active,
        last_login_at=updated_user.last_login_at.isoformat() if updated_user.last_login_at else None,
        created_at=updated_user.created_at.isoformat(),
        updated_at=updated_user.updated_at.isoformat()
    )

@router.post("/me/change-password")
def change_my_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario autenticado
    
    Requiere la contraseña actual para validación
    """
    UserController.change_password(
        db=db,
        user_id=str(current_user.id),
        password_data=password_data,
        current_user=current_user
    )
    
    return {"message": "Contraseña actualizada exitosamente"}

@router.post("/me/deactivate")
def deactivate_my_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Desactiva la cuenta del usuario autenticado
    
    **Advertencia:** Esta acción desactivará tu cuenta y cerrarás sesión
    """
    UserController.deactivate_user(
        db=db,
        user_id=str(current_user.id),
        current_user=current_user
    )
    
    return {"message": "Cuenta desactivada exitosamente"}

@router.get("/me/statistics", response_model=UserStatistics)
def get_my_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del usuario autenticado
    
    Incluye: número de mascotas, recordatorios, notificaciones, etc.
    """
    stats = UserController.get_user_statistics(
        db=db,
        user_id=str(current_user.id),
        current_user=current_user
    )
    
    return stats

# ============================================
# ENDPOINTS DE ADMINISTRACIÓN (solo admin)
# ============================================

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por username, email o nombre"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene todos los usuarios del sistema
    
    Permite filtrar por búsqueda y estado activo
    """
    users = UserController.get_all_users(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )
    
    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            timezone=user.timezone,
            role=user.role,
            email_verified=user.email_verified,
            is_active=user.is_active,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        for user in users
    ]

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un usuario por ID
    
    - **Usuarios normales:** Solo pueden ver su propio perfil
    - **Admins:** Pueden ver cualquier usuario
    """
    user = UserController.get_user_by_id(
        db=db,
        user_id=user_id,
        current_user=current_user
    )
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        timezone=user.timezone,
        role=user.role,
        email_verified=user.email_verified,
        is_active=user.is_active,
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza un usuario
    
    - **Usuarios normales:** Solo pueden actualizarse a sí mismos (sin cambiar rol/email_verified)
    - **Admins:** Pueden actualizar cualquier usuario con todos los campos
    """
    updated_user = UserController.update_user(
        db=db,
        user_id=user_id,
        user_data=user_data,
        current_user=current_user
    )
    
    return UserResponse(
        id=str(updated_user.id),
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        phone=updated_user.phone,
        timezone=updated_user.timezone,
        role=updated_user.role,
        email_verified=updated_user.email_verified,
        is_active=updated_user.is_active,
        last_login_at=updated_user.last_login_at.isoformat() if updated_user.last_login_at else None,
        created_at=updated_user.created_at.isoformat(),
        updated_at=updated_user.updated_at.isoformat()
    )

@router.post("/{user_id}/reactivate")
def reactivate_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Reactiva una cuenta de usuario desactivada
    """
    UserController.reactivate_user(
        db=db,
        user_id=user_id,
        current_user=current_user
    )
    
    return {"message": "Usuario reactivado exitosamente"}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Elimina permanentemente un usuario
    
    ⚠️ **ADVERTENCIA:** Esta acción es IRREVERSIBLE y eliminará todos los datos relacionados
    (mascotas, recordatorios, notificaciones, etc.)
    """
    UserController.delete_user(
        db=db,
        user_id=user_id,
        current_user=current_user
    )
    
    return None

@router.get("/{user_id}/statistics", response_model=UserStatistics)
def get_user_statistics(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de un usuario
    
    - **Usuarios normales:** Solo pueden ver sus propias estadísticas
    - **Admins:** Pueden ver las estadísticas de cualquier usuario
    """
    stats = UserController.get_user_statistics(
        db=db,
        user_id=user_id,
        current_user=current_user
    )
    
    return stats