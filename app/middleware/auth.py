from datetime import datetime
from typing import Optional
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.utils.security import decode_token
from app.utils.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    UserNotFoundException,
    InactiveAccountException,
    AccountLockedException
)

security = HTTPBearer()

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Middleware para obtener el usuario actual desde el token JWT
    """
    token = credentials.credentials
    
    # Decodificar token
    payload = decode_token(token)
    if not payload:
        raise InvalidTokenException()
    
    # Verificar tipo de token
    token_type = payload.get("type")
    if token_type != "access":
        raise InvalidTokenException()
    
    # Verificar expiración (exp ya viene como timestamp Unix)
    exp = payload.get("exp")
    if exp:
        current_timestamp = datetime.utcnow().timestamp()
        if current_timestamp > exp:
            raise TokenExpiredException()
    
    # Obtener user_id del payload
    user_id: str = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()
    
    # Buscar usuario en la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundException()
    
    # Verificar si la cuenta está activa
    if not user.is_active:
        raise InactiveAccountException()
    
    # Verificar si la cuenta está bloqueada
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise AccountLockedException(user.locked_until.isoformat())
    
    # Si el bloqueo expiró, resetear intentos fallidos
    if user.locked_until and user.locked_until <= datetime.utcnow():
        user.locked_until = None
        user.failed_attempts = 0
        db.commit()
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Middleware para verificar que el usuario esté activo
    """
    if not current_user.is_active:
        raise InactiveAccountException()
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Middleware para verificar que el usuario tenga email verificado
    """
    # Si quieres hacer obligatoria la verificación, descomenta lo siguiente:
    # if not current_user.email_verified:
    #     raise EmailNotVerifiedException()
    return current_user

def require_role(required_role: str):
    """
    Decorator para requerir un rol específico
    Uso: current_user: User = Depends(require_role("admin"))
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        from app.utils.exceptions import InsufficientPermissionsException
        
        if current_user.role != required_role:
            raise InsufficientPermissionsException()
        return current_user
    
    return role_checker

def require_any_role(allowed_roles: list[str]):
    """
    Decorator para requerir cualquiera de varios roles
    Uso: current_user: User = Depends(require_any_role(["admin", "moderator"]))
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        from app.utils.exceptions import InsufficientPermissionsException
        
        if current_user.role not in allowed_roles:
            raise InsufficientPermissionsException()
        return current_user
    
    return role_checker