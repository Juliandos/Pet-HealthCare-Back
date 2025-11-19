from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.middleware.auth import get_db, get_current_active_user
from app.controllers.auth import AuthController
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    UserProfile
)
from app.models import User

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema
    
    **Campos requeridos:**
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres, debe incluir mayúsculas, minúsculas y números)
    
    **Campos opcionales:**
    - **username**: Nombre de usuario único (se genera automáticamente si no se proporciona)
    - **full_name**: Nombre completo del usuario
    - **phone**: Teléfono
    - **timezone**: Zona horaria (por defecto UTC)
    
    **Ejemplo mínimo:**
    ```json
    {
        "email": "usuario@ejemplo.com",
        "password": "SecurePass123"
    }
    ```
    
    **Ejemplo completo:**
    ```json
    {
        "email": "usuario@ejemplo.com",
        "password": "SecurePass123",
        "username": "usuario123",
        "full_name": "Nombre Completo",
        "phone": "+57 300 123 4567",
        "timezone": "America/Bogota"
    }
    ```
    """
    user = AuthController.register_user(user_data, db)
    return UserProfile(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        timezone=user.timezone,
        role=user.role,
        email_verified=user.email_verified,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión con email y contraseña
    
    Retorna un access token (válido por 30 minutos) y un refresh token (válido por 7 días)
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    """
    tokens = AuthController.login_user(credentials, db)
    return tokens

@router.post("/refresh", response_model=dict)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Renueva el access token usando un refresh token
    
    - **refresh_token**: Refresh token válido obtenido en el login
    """
    new_tokens = AuthController.refresh_access_token(token_data.refresh_token, db)
    return new_tokens

@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cierra la sesión del usuario actual (invalida el refresh token)
    
    Requiere estar autenticado con un access token válido
    """
    AuthController.logout_user(current_user, db)
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/verify-email")
def verify_email(verification: EmailVerification, db: Session = Depends(get_db)):
    """
    Verifica el email del usuario usando el token enviado por correo
    
    - **token**: Token de verificación enviado al email
    """
    AuthController.verify_email(verification.token, db)
    return {"message": "Email verificado exitosamente"}

@router.post("/request-password-reset")
def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita un reseteo de contraseña enviando un email con el link
    
    - **email**: Email del usuario que quiere resetear su contraseña
    """
    message = AuthController.request_password_reset(reset_request.email, db)
    return {"message": message}

@router.post("/reset-password")
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    Resetea la contraseña usando el token recibido por email
    
    - **token**: Token recibido en el email
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, debe incluir mayúsculas, minúsculas y números)
    """
    AuthController.reset_password(reset_data.token, reset_data.new_password, db)
    return {"message": "Contraseña actualizada exitosamente"}

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene el perfil del usuario autenticado actual
    
    Requiere estar autenticado con un access token válido
    """
    return UserProfile(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        timezone=current_user.timezone,
        role=current_user.role,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )

@router.get("/validate-token")
def validate_token(current_user: User = Depends(get_current_active_user)):
    """
    Valida si un token es válido y retorna información básica del usuario
    
    Útil para validar tokens en el frontend
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role
    }

@router.get("/dev/get-verification-token/{email}")
def get_verification_token_dev(email: str, db: Session = Depends(get_db)):
    """
    ⚠️ SOLO PARA DESARROLLO ⚠️
    Obtiene el token de verificación de un usuario por email
    
    **ELIMINAR EN PRODUCCIÓN**
    
    - **email**: Email del usuario
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        from app.utils.exceptions import UserNotFoundException
        raise UserNotFoundException()
    
    return {
        "email": user.email,
        "verification_token": user.verification_token,
        "email_verified": user.email_verified,
        "instructions": f"Usa este token en POST /auth/verify-email con el body: {{\"token\": \"{user.verification_token}\"}}"
    }

@router.post("/dev/decode-token")
def decode_token_dev(token: str):
    """
    ⚠️ SOLO PARA DESARROLLO ⚠️
    Decodifica un JWT para ver su contenido
    
    **ELIMINAR EN PRODUCCIÓN**
    """
    from app.utils.security import decode_token
    from datetime import datetime
    
    payload = decode_token(token)
    
    if not payload:
        return {"error": "Token inválido o corrupto"}
    
    # Información adicional sobre expiración
    exp = payload.get("exp")
    iat = payload.get("iat")
    current_time = datetime.utcnow().timestamp()
    
    result = {
        "payload": payload,
        "debug_info": {
            "current_timestamp": current_time,
            "issued_at_timestamp": iat,
            "expires_at_timestamp": exp,
            "is_expired": current_time > exp if exp else None,
            "time_until_expiry_seconds": exp - current_time if exp else None
        }
    }
    
    if exp:
        result["debug_info"]["issued_at_human"] = datetime.fromtimestamp(iat).isoformat() if iat else None
        result["debug_info"]["expires_at_human"] = datetime.fromtimestamp(exp).isoformat()
        result["debug_info"]["current_time_human"] = datetime.utcnow().isoformat()
    
    return result