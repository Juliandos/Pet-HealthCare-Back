# ========================================
# app/controllers/audit_logs.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.models import AuditLog, User
from app.schemas.audit_logs import AuditLogCreate, AuditLogFilter
from fastapi import HTTPException, status

class AuditLogController:
    """Controlador para logs de auditoría"""
    
    @staticmethod
    def get_all(
        db: Session,
        current_user: User,
        filters: Optional[AuditLogFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Obtiene todos los logs de auditoría con filtros
        Solo admins pueden ver todos los logs
        Usuarios normales solo ven sus propios logs
        """
        query = db.query(AuditLog)
        
        # Si no es admin, solo puede ver sus propios logs
        if current_user.role != "admin":
            query = query.filter(AuditLog.actor_user_id == current_user.id)
        
        # Aplicar filtros si se proporcionan
        if filters:
            if filters.actor_user_id:
                query = query.filter(AuditLog.actor_user_id == filters.actor_user_id)
            
            if filters.action:
                query = query.filter(AuditLog.action.ilike(f"%{filters.action}%"))
            
            if filters.object_type:
                query = query.filter(AuditLog.object_type == filters.object_type)
            
            if filters.object_id:
                query = query.filter(AuditLog.object_id == filters.object_id)
            
            if filters.date_from:
                query = query.filter(AuditLog.created_at >= filters.date_from)
            
            if filters.date_to:
                query = query.filter(AuditLog.created_at <= filters.date_to)
        
        return query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, audit_log_id: str, current_user: User) -> AuditLog:
        """Obtiene un log específico por ID"""
        audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
        
        if not audit_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log de auditoría no encontrado"
            )
        
        # Si no es admin, solo puede ver sus propios logs
        if current_user.role != "admin" and str(audit_log.actor_user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este log"
            )
        
        return audit_log
    
    @staticmethod
    def create(db: Session, data: AuditLogCreate) -> AuditLog:
        """
        Crea un nuevo log de auditoría
        Nota: Los logs normalmente se crean automáticamente por el sistema
        """
        new_log = AuditLog(**data.model_dump())
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
    
    @staticmethod
    def get_user_activity(
        db: Session,
        user_id: str,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Obtiene toda la actividad de un usuario específico"""
        # Solo admin o el propio usuario pueden ver su actividad
        if current_user.role != "admin" and str(current_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta actividad"
            )
        
        return db.query(AuditLog).filter(
            AuditLog.actor_user_id == user_id
        ).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_object_history(
        db: Session,
        object_type: str,
        object_id: str,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Obtiene el historial de cambios de un objeto específico"""
        # Solo admin puede ver historial de objetos
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este historial"
            )
        
        return db.query(AuditLog).filter(
            and_(
                AuditLog.object_type == object_type,
                AuditLog.object_id == object_id
            )
        ).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_statistics(db: Session, current_user: User) -> dict:
        """Obtiene estadísticas de los logs de auditoría"""
        from sqlalchemy import func
        
        # Solo admin puede ver estadísticas globales
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver estas estadísticas"
            )
        
        # Total de logs
        total_logs = db.query(func.count(AuditLog.id)).scalar()
        
        # Logs por acción (top 10)
        actions_stats = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).order_by(desc('count')).limit(10).all()
        
        # Logs por tipo de objeto (top 10)
        object_types_stats = db.query(
            AuditLog.object_type,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.object_type).order_by(desc('count')).limit(10).all()
        
        # Usuarios más activos (top 10)
        active_users = db.query(
            AuditLog.actor_user_id,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.actor_user_id).order_by(desc('count')).limit(10).all()
        
        # Logs de hoy
        from datetime import date
        today = date.today()
        logs_today = db.query(func.count(AuditLog.id)).filter(
            func.date(AuditLog.created_at) == today
        ).scalar()
        
        return {
            "total_logs": total_logs,
            "logs_today": logs_today,
            "top_actions": [
                {"action": action, "count": count}
                for action, count in actions_stats
            ],
            "top_object_types": [
                {"object_type": obj_type, "count": count}
                for obj_type, count in object_types_stats
            ],
            "most_active_users": [
                {"user_id": str(user_id), "activity_count": count}
                for user_id, count in active_users
            ]
        }
    
    @staticmethod
    def delete_old_logs(db: Session, days: int, current_user: User) -> int:
        """
        Elimina logs antiguos (solo admin)
        Útil para mantenimiento y GDPR compliance
        """
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar logs"
            )
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        # Log de la eliminación
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="AUDIT_LOGS_PURGED",
            object_type="AuditLog",
            meta={
                "deleted_count": deleted_count,
                "days_older_than": days,
                "cutoff_date": cutoff_date.isoformat()
            }
        )
        db.add(audit)
        db.commit()
        
        return deleted_count