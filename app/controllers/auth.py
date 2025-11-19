from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, PasswordReset, AuditLog
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    generate_password_reset_token
)
from app.utils.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    AccountLockedException,
    EmailNotVerifiedException,
    InactiveAccountException,
    InvalidTokenException
)
from app.config import settings
from app.services.email_service import EmailService

class AuthController:
    """Controlador para operaciones de autenticación"""
    
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> User:
        """Registra un nuevo usuario"""
        
        # Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise UserAlreadyExistsException("email")
        
        # Verificar si el username ya existe (solo si se proporcionó)
        if user_data.username:
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise UserAlreadyExistsException("username")
        
        # Generar username automático si no se proporcionó
        username = user_data.username
        if not username:
            # Generar username basado en email (antes del @)
            base_username = user_data.email.split('@')[0]
            # Si ya existe, agregar un número aleatorio
            username = base_username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
        
        # Crear nuevo usuario
        verification_token = generate_verification_token()
        new_user = User(
            username=username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            timezone=user_data.timezone or "UTC",
            verification_token=verification_token,
            email_verified=False,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=new_user.id,
            action="USER_REGISTERED",
            object_type="User",
            object_id=new_user.id,
            meta={"email": new_user.email, "username": new_user.username}
        )
        db.add(audit)
        db.commit()
        
        # Enviar email de verificación
        try:
            EmailService.send_verification_email(
                email=new_user.email,
                username=new_user.username,
                token=verification_token
            )
            print(f"✅ Email de verificación enviado a {new_user.email}")
        except Exception as e:
            print(f"⚠️ Error enviando email de verificación: {str(e)}")
            # No fallar el registro si el email no se envía
        
        return new_user
    
    @staticmethod
    def login_user(credentials: UserLogin, db: Session) -> dict:
        """Autentica un usuario y retorna tokens"""
        
        # Buscar usuario por email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise InvalidCredentialsException()
        
        # Verificar si la cuenta está bloqueada
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise AccountLockedException(user.locked_until.isoformat())
        
        # Resetear bloqueo si ya expiró
        if user.locked_until and user.locked_until <= datetime.utcnow():
            user.locked_until = None
            user.failed_attempts = 0
            db.commit()
        
        # Verificar contraseña
        if not verify_password(credentials.password, user.hashed_password):
            # Incrementar intentos fallidos
            user.failed_attempts += 1
            
            # Bloquear cuenta si excede el máximo de intentos
            if user.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCK_MINUTES)
                db.commit()
                raise AccountLockedException(user.locked_until.isoformat())
            
            db.commit()
            raise InvalidCredentialsException()
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise InactiveAccountException()
        
        # Verificar si el email está verificado
        if not user.email_verified:
            raise EmailNotVerifiedException()
        
        # Login exitoso - resetear intentos fallidos
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        
        # Generar tokens
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Guardar refresh token en la base de datos
        user.refresh_token = refresh_token
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=user.id,
            action="USER_LOGIN",
            object_type="User",
            object_id=user.id,
            meta={"email": user.email}
        )
        db.add(audit)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> dict:
        """Genera un nuevo access token usando el refresh token"""
        
        # Decodificar refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidTokenException()
        
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException()
        
        # Buscar usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException()
        
        # Verificar que el refresh token coincida
        if user.refresh_token != refresh_token:
            raise InvalidTokenException()
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise InactiveAccountException()
        
        # Generar nuevo access token
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        new_access_token = create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def verify_email(token: str, db: Session) -> bool:
        """Verifica el email del usuario"""
        
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            raise InvalidTokenException()
        
        user.email_verified = True
        user.verification_token = None
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=user.id,
            action="EMAIL_VERIFIED",
            object_type="User",
            object_id=user.id
        )
        db.add(audit)
        db.commit()
        
        return True
    
    @staticmethod
    def request_password_reset(email: str, db: Session) -> str:
        """Solicita un reseteo de contraseña"""
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Por seguridad, no revelar que el usuario no existe
            return "Si el email existe, recibirás un link de reseteo"
        
        # Generar token de reseteo
        reset_token = generate_password_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)
        
        # Guardar token en la base de datos
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at,
            used=False
        )
        db.add(password_reset)
        db.commit()
        
        # Enviar email de reseteo
        try:
            EmailService.send_password_reset_email(
                email=user.email,
                username=user.username,
                token=reset_token
            )
            print(f"✅ Email de reseteo enviado a {user.email}")
        except Exception as e:
            print(f"⚠️ Error enviando email de reseteo: {str(e)}")
        
        return "Si el email existe, recibirás un link de reseteo"
    
    @staticmethod
    def reset_password(token: str, new_password: str, db: Session) -> bool:
        """Resetea la contraseña del usuario"""
        
        # Buscar token de reseteo
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.used == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).first()
        
        if not reset:
            raise InvalidTokenException()
        
        # Actualizar contraseña
        user = db.query(User).filter(User.id == reset.user_id).first()
        if not user:
            raise UserNotFoundException()
        
        user.hashed_password = hash_password(new_password)
        reset.used = True
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=user.id,
            action="PASSWORD_RESET",
            object_type="User",
            object_id=user.id
        )
        db.add(audit)
        db.commit()
        
        return True
    
    @staticmethod
    def logout_user(user: User, db: Session) -> bool:
        """Cierra sesión del usuario (invalida refresh token)"""
        
        user.refresh_token = None
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=user.id,
            action="USER_LOGOUT",
            object_type="User",
            object_id=user.id
        )
        db.add(audit)
        db.commit()
        
        return True