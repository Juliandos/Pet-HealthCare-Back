from fastapi import HTTPException, status

class AuthException(HTTPException):
    """Excepción base para errores de autenticación"""
    pass

class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o corrupto",
            headers={"WWW-Authenticate": "Bearer"},
        )

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

class UserAlreadyExistsException(HTTPException):
    def __init__(self, field: str = "email"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario con ese {field}"
        )

class AccountLockedException(AuthException):
    def __init__(self, locked_until: str):
        super().__init__(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cuenta bloqueada temporalmente hasta {locked_until} por múltiples intentos fallidos"
        )

class EmailNotVerifiedException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu email antes de iniciar sesión"
        )

class InactiveAccountException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está inactiva. Contacta al soporte"
        )

class InsufficientPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para realizar esta acción"
        )