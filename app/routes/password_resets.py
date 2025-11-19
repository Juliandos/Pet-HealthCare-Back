# ========================================
# app/routes/password_resets.py
# ========================================
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.middleware.auth import get_db, get_current_active_user, require_role
from app.controllers.password_resets import PasswordResetController
from app.schemas.password_resets import (
    PasswordResetResponse,
    PasswordResetWithUser,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetStats
)
from app.models import User

router = APIRouter(prefix="/password-resets", tags=["Password Resets"])

# ============================================
# ENDPOINTS PÚBLICOS (sin autenticación)
# ============================================

@router.post("/request", status_code=status.HTTP_200_OK)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    **[PÚBLICO]** Solicita un reseteo de contraseña
    
    Envía un email con un link para resetear la contraseña.
    Por seguridad, siempre retorna el mismo mensaje independientemente
    de si el email existe o no.
    
    **Rate limit:** Máximo 1 solicitud cada 5 minutos por email
    
    **Ejemplo:**
    ```json
    {
        "email": "usuario@ejemplo.com"
    }
    ```
    """
    result = PasswordResetController.request_reset(
        email=data.email,
        db=db
    )
    return result

@router.post("/confirm", status_code=status.HTTP_200_OK)
def confirm_password_reset(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    **[PÚBLICO]** Confirma el reseteo y establece nueva contraseña
    
    Usa el token recibido por email para cambiar la contraseña.
    
    **Ejemplo:**
    ```json
    {
        "token": "token-largo-recibido-por-email",
        "new_password": "NuevaPassword123"
    }
    ```
    
    **Requisitos de la contraseña:**
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    """
    result = PasswordResetController.confirm_reset(
        token=data.token,
        new_password=data.new_password,
        db=db
    )
    return result

@router.get("/validate/{token}", status_code=status.HTTP_200_OK)
def validate_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    **[PÚBLICO]** Valida si un token de reseteo es válido
    
    Útil para validar el token antes de mostrar el formulario
    de cambio de contraseña en el frontend.
    
    **Retorna:**
    - `valid`: true/false
    - `reason`: Razón si no es válido
    - `expires_at`: Fecha de expiración si es válido
    """
    result = PasswordResetController.validate_token(
        token=token,
        db=db
    )
    return result

# ============================================
# ENDPOINTS DE ADMINISTRACIÓN (solo admin)
# ============================================

@router.get("/", response_model=List[PasswordResetWithUser])
def get_all_password_resets(
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    is_used: Optional[bool] = Query(None, description="Filtrar por tokens usados/no usados"),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene todos los password resets del sistema
    
    Permite filtrar por usuario y estado (usado/no usado).
    """
    resets = PasswordResetController.get_all(
        db=db,
        current_user=current_user,
        user_id=user_id,
        is_used=is_used,
        skip=skip,
        limit=limit
    )
    
    # Enriquecer con información del usuario
    enriched = []
    for reset in resets:
        enriched.append(PasswordResetWithUser(
            id=str(reset.id),
            user_id=str(reset.user_id),
            token=reset.token,
            expires_at=reset.expires_at,
            used=reset.used,
            created_at=reset.created_at,
            updated_at=reset.updated_at,
            user_email=reset.user.email if reset.user else None,
            user_username=reset.user.username if reset.user else None
        ))
    
    return enriched

@router.get("/stats", response_model=PasswordResetStats)
def get_password_reset_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene estadísticas de password resets
    
    Incluye:
    - Total de solicitudes
    - Tokens usados
    - Tokens expirados
    - Tokens pendientes
    - Solicitudes últimas 24 horas
    - Solicitudes última semana
    """
    return PasswordResetController.get_statistics(
        db=db,
        current_user=current_user
    )

@router.get("/{reset_id}", response_model=PasswordResetWithUser)
def get_password_reset_by_id(
    reset_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene un password reset específico por ID
    """
    reset = PasswordResetController.get_by_id(
        db=db,
        reset_id=reset_id,
        current_user=current_user
    )
    
    return PasswordResetWithUser(
        id=str(reset.id),
        user_id=str(reset.user_id),
        token=reset.token,
        expires_at=reset.expires_at,
        used=reset.used,
        created_at=reset.created_at,
        updated_at=reset.updated_at,
        user_email=reset.user.email if reset.user else None,
        user_username=reset.user.username if reset.user else None
    )

@router.delete("/{reset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_password_reset(
    reset_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Elimina un password reset específico
    
    Útil para limpiar tokens específicos manualmente.
    """
    PasswordResetController.delete_reset(
        reset_id=reset_id,
        db=db,
        current_user=current_user
    )
    return None

@router.post("/cleanup", status_code=status.HTTP_200_OK)
def cleanup_expired_resets(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Elimina todos los tokens expirados
    
    Útil para mantenimiento de base de datos.
    """
    deleted_count = PasswordResetController.cleanup_expired(
        db=db,
        current_user=current_user
    )
    
    return {
        "message": f"Se eliminaron {deleted_count} tokens expirados",
        "deleted_count": deleted_count
    }

@router.get("/user/{user_id}/history", response_model=List[PasswordResetResponse])
def get_user_reset_history(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    **[ADMIN]** Obtiene el historial de password resets de un usuario
    
    Útil para auditoría y detectar patrones sospechosos.
    """
    resets = PasswordResetController.get_all(
        db=db,
        current_user=current_user,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    return [
        PasswordResetResponse(
            id=str(reset.id),
            user_id=str(reset.user_id),
            token=reset.token,
            expires_at=reset.expires_at,
            used=reset.used,
            created_at=reset.created_at,
            updated_at=reset.updated_at
        )
        for reset in resets
    ]