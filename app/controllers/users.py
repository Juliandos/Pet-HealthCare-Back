from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.models import User, AuditLog
from app.schemas.users import UserUpdate, UserChangePassword
from app.utils.security import hash_password, verify_password
from app.utils.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from fastapi import HTTPException, status

class UserController:
    """Controlador para operaciones con usuarios"""
    
    @staticmethod
    def get_all_users(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        Obtiene todos los usuarios (solo admins)
        Permite filtrar por búsqueda y estado activo
        """
        # Solo admin puede ver todos los usuarios
        if current_user.role != "admin":
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        query = db.query(User)
        
        # Filtrar por búsqueda (username, email, full_name)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_filter),
                    User.email.ilike(search_filter),
                    User.full_name.ilike(search_filter)
                )
            )
        
        # Filtrar por estado activo
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str, current_user: User) -> User:
        """
        Obtiene un usuario por ID
        Solo admins pueden ver otros usuarios, users solo pueden verse a sí mismos
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException()
        
        # Solo admin puede ver otros usuarios
        if current_user.role != "admin" and str(current_user.id) != user_id:
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        return user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        user_data: UserUpdate,
        current_user: User
    ) -> User:
        """
        Actualiza un usuario
        Users pueden actualizarse a sí mismos (excepto rol y email_verified)
        Admins pueden actualizar cualquier usuario
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException()
        
        # Verificar permisos
        is_self = str(current_user.id) == user_id
        is_admin = current_user.role == "admin"
        
        if not is_self and not is_admin:
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        # Obtener datos a actualizar
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Si NO es admin, no puede cambiar rol ni email_verified
        if not is_admin:
            update_data.pop('role', None)
            update_data.pop('email_verified', None)
            update_data.pop('is_active', None)
        
        # Verificar si el email ya existe (si se está cambiando)
        if 'email' in update_data and update_data['email'] != user.email:
            existing_email = db.query(User).filter(
                User.email == update_data['email'],
                User.id != user_id
            ).first()
            if existing_email:
                raise UserAlreadyExistsException("email")
        
        # Verificar si el username ya existe (si se está cambiando)
        if 'username' in update_data and update_data['username'] != user.username:
            existing_username = db.query(User).filter(
                User.username == update_data['username'],
                User.id != user_id
            ).first()
            if existing_username:
                raise UserAlreadyExistsException("username")
        
        # Actualizar campos
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="USER_UPDATED",
            object_type="User",
            object_id=user.id,
            meta={
                "updated_fields": list(update_data.keys()),
                "updated_by": "self" if is_self else "admin"
            }
        )
        db.add(audit)
        db.commit()
        
        return user
    
    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        password_data: UserChangePassword,
        current_user: User
    ) -> bool:
        """
        Cambia la contraseña de un usuario
        Requiere contraseña actual para validación
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException()
        
        # Solo el usuario puede cambiar su propia contraseña
        if str(current_user.id) != user_id:
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        # Verificar contraseña actual
        if not verify_password(password_data.current_password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # Actualizar contraseña
        user.hashed_password = hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        # Invalidar refresh token por seguridad
        user.refresh_token = None
        
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="PASSWORD_CHANGED",
            object_type="User",
            object_id=user.id
        )
        db.add(audit)
        db.commit()
        
        return True
    
    @staticmethod
    def deactivate_user(db: Session, user_id: str, current_user: User) -> bool:
        """
        Desactiva una cuenta de usuario
        Solo admin puede desactivar otros usuarios
        Usuario puede desactivar su propia cuenta
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException()
        
        # Verificar permisos
        is_self = str(current_user.id) == user_id
        is_admin = current_user.role == "admin"
        
        if not is_self and not is_admin:
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        # No se puede desactivar a sí mismo siendo admin (evitar lockout)
        if is_self and is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los administradores no pueden desactivar su propia cuenta"
            )
        
        user.is_active = False
        user.refresh_token = None  # Invalidar sesiones
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="USER_DEACTIVATED",
            object_type="User",
            object_id=user.id,
            meta={"deactivated_by": "self" if is_self else "admin"}
        )
        db.add(audit)
        db.commit()
        
        return True
    
    @staticmethod
    def reactivate_user(db: Session, user_id: str, current_user: User) -> bool:
        """
        Reactiva una cuenta de usuario (solo admin)
        """
        if current_user.role != "admin":
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException()
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="USER_REACTIVATED",
            object_type="User",
            object_id=user.id
        )
        db.add(audit)
        db.commit()
        
        return True
    
    @staticmethod
    def delete_user(db: Session, user_id: str, current_user: User) -> bool:
        """
        Elimina permanentemente un usuario (solo admin)
        ⚠️ Esta acción es IRREVERSIBLE y eliminará todos los datos relacionados
        """
        if current_user.role != "admin":
            from app.utils.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException()
        
        # No permitir eliminar la propia cuenta de admin
        if str(current_user.id) == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu propia cuenta de administrador"
            )
        
        # Log de auditoría ANTES de eliminar
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="USER_DELETED",
            object_type="User",
            object_id=user.id,
            meta={
                "deleted_user_email": user.email,
                "deleted_user_username": user.username
            }
        )
        db.add(audit)
        
        # Eliminar usuario (cascade eliminará todos los datos relacionados)
        db.delete(user)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_statistics(db: Session, user_id: str, current_user: User) -> dict:
        """
        Obtiene estadísticas del usuario (número de mascotas, recordatorios, etc.)
        """
        user = UserController.get_user_by_id(db, user_id, current_user)
        
        from app.models import Pet, Reminder, Notification
        
        stats = {
            "user_id": str(user.id),
            "username": user.username,
            "total_pets": db.query(Pet).filter(Pet.owner_id == user.id).count(),
            "total_reminders": db.query(Reminder).filter(Reminder.owner_id == user.id).count(),
            "active_reminders": db.query(Reminder).filter(
                Reminder.owner_id == user.id,
                Reminder.is_active == True
            ).count(),
            "total_notifications": db.query(Notification).filter(Notification.owner_id == user.id).count(),
            "account_created": user.created_at.isoformat(),
            "last_login": user.last_login_at.isoformat() if user.last_login_at else None
        }
        
        return stats