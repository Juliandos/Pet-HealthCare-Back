from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import hashlib
from jose import JWTError, jwt
import bcrypt
from app.config import settings

def hash_password(password: str) -> str:
    """
    Encripta una contraseña usando bcrypt.
    Trunca la contraseña a 72 bytes si es necesario (límite de bcrypt).
    """
    # Convertir a bytes y truncar a 72 bytes si es necesario
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Hash la contraseña primero si excede 72 bytes
        password_bytes = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
    
    # Generar salt y hashear
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    Maneja el límite de 72 bytes de bcrypt.
    """
    try:
        # Convertir a bytes y truncar si es necesario
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            # Hash la contraseña primero si excede 72 bytes
            password_bytes = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
        
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Convertir a timestamp Unix para el payload
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Crea un token de refresco JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Convertir a timestamp Unix para el payload
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica y valida un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_verification_token() -> str:
    """Genera un token seguro para verificación de email"""
    return secrets.token_urlsafe(32)

def generate_password_reset_token() -> str:
    """Genera un token seguro para reseteo de contraseña"""
    return secrets.token_urlsafe(32)