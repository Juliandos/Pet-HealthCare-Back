# ========================================
# app/controllers/password_resets.py
# ========================================
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from app.models import PasswordReset, User, AuditLog
from app.schemas.password_resets import (
    PasswordResetCreate,
    PasswordResetUpdate,
    PasswordResetStats
)
from app.utils.security import generate_password_reset_token, hash_password
from app.services.email_service import EmailService
from app.config import settings
from fastapi import HTTPException, status

class PasswordResetController:
    """Controlador para operaciones de password reset"""
    
    @staticmethod
    def get_all(
        db: Session,
        current_user: User,
        user_id: Optional[str] = None,
        is_used: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PasswordReset]:
        """
        Obtiene todos los password resets (solo admin)
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario actual (debe ser admin)
            user_id: Filtrar por usuario específico
            is_used: Filtrar por tokens usados/no usados
            skip: Registros a omitir
            limit: Máximo de registros
        
        Returns:
            Lista de password resets
        """
        # Solo admin puede ver todos los resets
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver password resets"
            )
        
        query = db.query(PasswordReset)
        
        if user_id:
            query = query.filter(PasswordReset.user_id == user_id)
        
        if is_used is not None:
            query = query.filter(PasswordReset.used == is_used)
        
        return query.order_by(desc(PasswordReset.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, reset_id: str, current_user: User) -> PasswordReset:
        """
        Obtiene un password reset por ID (solo admin)
        
        Args:
            db: Sesión de base de datos
            reset_id: ID del reset
            current_user: Usuario actual (debe ser admin)
        
        Returns:
            Password reset encontrado
        """
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este reset"
            )
        
        reset = db.query(PasswordReset).filter(PasswordReset.id == reset_id).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Password reset no encontrado"
            )
        
        return reset
    
    @staticmethod
    def request_reset(email: str, db: Session) -> dict:
        """
        Solicita un reseteo de contraseña
        
        Args:
            email: Email del usuario
            db: Sesión de base de datos
        
        Returns:
            Mensaje de confirmación
        """
        # Buscar usuario
        user = db.query(User).filter(User.email == email).first()
        
        # Por seguridad, siempre retornar el mismo mensaje
        if not user:
            return {
                "message": "Si el email existe, recibirás un link de reseteo",
                "sent": False
            }
        
        # Verificar si ya hay un reset pendiente reciente (últimos 5 minutos)
        recent_reset = db.query(PasswordReset).filter(
            and_(
                PasswordReset.user_id == user.id,
                PasswordReset.used == False,
                PasswordReset.created_at >= datetime.utcnow() - timedelta(minutes=5)
            )
        ).first()
        
        if recent_reset:
            return {
                "message": "Ya enviamos un email recientemente. Revisa tu bandeja de entrada",
                "sent": False
            }
        
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
        db.refresh(password_reset)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=user.id,
            action="PASSWORD_RESET_REQUESTED",
            object_type="PasswordReset",
            object_id=password_reset.id,
            meta={"email": user.email}
        )
        db.add(audit)
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
        
        return {
            "message": "Si el email existe, recibirás un link de reseteo",
            "sent": True
        }
    
    @staticmethod
    def confirm_reset(token: str, new_password: str, db: Session) -> dict:
        """
        Confirma el reseteo y cambia la contraseña
        
        Args:
            token: Token de reseteo
            new_password: Nueva contraseña
            db: Sesión de base de datos
        
        Returns:
            Mensaje de confirmación
        """
        # Buscar token de reseteo válido
        reset = db.query(PasswordReset).filter(
            and_(
                PasswordReset.token == token,
                PasswordReset.used == False,
                PasswordReset.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )
        
        # Buscar usuario
        user = db.query(User).filter(User.id == reset.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar contraseña
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        # Marcar token como usado
        reset.used = True
        reset.updated_at = datetime.utcnow()
        
        # Invalidar refresh token por seguridad
        user.refresh_token = None
        
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=user.id,
            action="PASSWORD_RESET_COMPLETED",
            object_type="PasswordReset",
            object_id=reset.id,
            meta={"email": user.email}
        )
        db.add(audit)
        db.commit()
        
        return {
            "message": "Contraseña actualizada exitosamente",
            "success": True
        }
    
    @staticmethod
    def validate_token(token: str, db: Session) -> dict:
        """
        Valida si un token es válido
        
        Args:
            token: Token a validar
            db: Sesión de base de datos
        
        Returns:
            Estado del token
        """
        reset = db.query(PasswordReset).filter(PasswordReset.token == token).first()
        
        if not reset:
            return {
                "valid": False,
                "reason": "Token no encontrado"
            }
        
        if reset.used:
            return {
                "valid": False,
                "reason": "Token ya usado"
            }
        
        if reset.expires_at <= datetime.utcnow():
            return {
                "valid": False,
                "reason": "Token expirado",
                "expired_at": reset.expires_at.isoformat()
            }
        
        return {
            "valid": True,
            "expires_at": reset.expires_at.isoformat()
        }
    
    @staticmethod
    def delete_reset(reset_id: str, db: Session, current_user: User) -> bool:
        """
        Elimina un password reset (solo admin)
        
        Args:
            reset_id: ID del reset
            db: Sesión de base de datos
            current_user: Usuario actual (debe ser admin)
        
        Returns:
            True si se eliminó
        """
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar resets"
            )
        
        reset = db.query(PasswordReset).filter(PasswordReset.id == reset_id).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Password reset no encontrado"
            )
        
        db.delete(reset)
        db.commit()
        
        return True
    
    @staticmethod
    def cleanup_expired(db: Session, current_user: User) -> int:
        """
        Elimina tokens expirados (solo admin)
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario actual (debe ser admin)
        
        Returns:
            Número de tokens eliminados
        """
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para limpiar resets"
            )
        
        deleted_count = db.query(PasswordReset).filter(
            PasswordReset.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PASSWORD_RESETS_CLEANED",
            object_type="PasswordReset",
            meta={"deleted_count": deleted_count}
        )
        db.add(audit)
        db.commit()
        
        return deleted_count
    
    @staticmethod
    def get_statistics(db: Session, current_user: User) -> PasswordResetStats:
        """
        Obtiene estadísticas de password resets (solo admin)
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario actual (debe ser admin)
        
        Returns:
            Estadísticas
        """
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver estadísticas"
            )
        
        now = datetime.utcnow()
        
        total = db.query(func.count(PasswordReset.id)).scalar()
        used = db.query(func.count(PasswordReset.id)).filter(PasswordReset.used == True).scalar()
        expired = db.query(func.count(PasswordReset.id)).filter(
            and_(
                PasswordReset.used == False,
                PasswordReset.expires_at < now
            )
        ).scalar()
        pending = db.query(func.count(PasswordReset.id)).filter(
            and_(
                PasswordReset.used == False,
                PasswordReset.expires_at >= now
            )
        ).scalar()
        
        last_24h = db.query(func.count(PasswordReset.id)).filter(
            PasswordReset.created_at >= now - timedelta(hours=24)
        ).scalar()
        
        last_week = db.query(func.count(PasswordReset.id)).filter(
            PasswordReset.created_at >= now - timedelta(days=7)
        ).scalar()
        
        return PasswordResetStats(
            total_requests=total or 0,
            used_tokens=used or 0,
            expired_tokens=expired or 0,
            pending_tokens=pending or 0,
            requests_last_24h=last_24h or 0,
            requests_last_week=last_week or 0
        )