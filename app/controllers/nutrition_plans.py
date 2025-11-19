# ========================================
# app/controllers/nutrition_plans.py
# ========================================
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models import NutritionPlan, Pet, User, AuditLog, Meal
from app.schemas.nutrition_plans import NutritionPlanCreate, NutritionPlanUpdate
from fastapi import HTTPException, status

class NutritionPlanController:
    """Controlador para operaciones con planes de nutrición"""
    
    @staticmethod
    def get_all(
        db: Session,
        current_user: User,
        pet_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[NutritionPlan]:
        """
        Obtiene todos los planes de nutrición del usuario
        
        Args:
            db: Sesión de base de datos
            current_user: Usuario autenticado
            pet_id: Filtrar por mascota específica (opcional)
            skip: Registros a omitir
            limit: Máximo de registros
        
        Returns:
            Lista de planes de nutrición
        """
        query = db.query(NutritionPlan).join(Pet).filter(
            Pet.owner_id == current_user.id
        )
        
        if pet_id:
            query = query.filter(NutritionPlan.pet_id == pet_id)
        
        return query.order_by(desc(NutritionPlan.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, plan_id: str, current_user: User) -> NutritionPlan:
        """
        Obtiene un plan de nutrición específico por ID
        
        Args:
            db: Sesión de base de datos
            plan_id: ID del plan
            current_user: Usuario autenticado
        
        Returns:
            Plan de nutrición encontrado
        
        Raises:
            HTTPException: Si no se encuentra el plan
        """
        plan = db.query(NutritionPlan).join(Pet).filter(
            NutritionPlan.id == plan_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan de nutrición no encontrado"
            )
        
        return plan
    
    @staticmethod
    def create(db: Session, data: NutritionPlanCreate, current_user: User) -> NutritionPlan:
        """
        Crea un nuevo plan de nutrición
        
        Args:
            db: Sesión de base de datos
            data: Datos del plan
            current_user: Usuario autenticado
        
        Returns:
            Plan de nutrición creado
        
        Raises:
            HTTPException: Si la mascota no existe o no pertenece al usuario
        """
        # Verificar que la mascota existe y pertenece al usuario
        pet = db.query(Pet).filter(
            Pet.id == data.pet_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )
        
        # Crear plan
        new_plan = NutritionPlan(**data.model_dump())
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="NUTRITION_PLAN_CREATED",
            object_type="NutritionPlan",
            object_id=new_plan.id,
            meta={
                "plan_name": new_plan.name,
                "pet_id": str(new_plan.pet_id),
                "calories_per_day": new_plan.calories_per_day
            }
        )
        db.add(audit)
        db.commit()
        
        return new_plan
    
    @staticmethod
    def update(
        db: Session,
        plan_id: str,
        data: NutritionPlanUpdate,
        current_user: User
    ) -> NutritionPlan:
        """
        Actualiza un plan de nutrición existente
        
        Args:
            db: Sesión de base de datos
            plan_id: ID del plan
            data: Datos a actualizar
            current_user: Usuario autenticado
        
        Returns:
            Plan actualizado
        """
        plan = NutritionPlanController.get_by_id(db, plan_id, current_user)
        
        # Actualizar solo campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        
        # Guardar cambios para auditoría
        modified_fields = []
        for field, value in update_data.items():
            if value is not None and getattr(plan, field) != value:
                modified_fields.append(field)
                setattr(plan, field, value)
        
        if modified_fields:
            plan.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(plan)
            
            # Log de auditoría
            audit = AuditLog(
                actor_user_id=current_user.id,
                action="NUTRITION_PLAN_UPDATED",
                object_type="NutritionPlan",
                object_id=plan.id,
                meta={
                    "updated_fields": modified_fields,
                    "plan_name": plan.name
                }
            )
            db.add(audit)
            db.commit()
        
        return plan
    
    @staticmethod
    def delete(db: Session, plan_id: str, current_user: User) -> bool:
        """
        Elimina un plan de nutrición
        
        Args:
            db: Sesión de base de datos
            plan_id: ID del plan
            current_user: Usuario autenticado
        
        Returns:
            True si se eliminó correctamente
        
        Note:
            Esto también eliminará las comidas asociadas si tienen plan_id
        """
        plan = NutritionPlanController.get_by_id(db, plan_id, current_user)
        
        # Guardar info para auditoría
        plan_info = {
            "plan_name": plan.name,
            "pet_id": str(plan.pet_id),
            "calories_per_day": plan.calories_per_day
        }
        
        # Log de auditoría antes de eliminar
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="NUTRITION_PLAN_DELETED",
            object_type="NutritionPlan",
            object_id=plan.id,
            meta=plan_info
        )
        db.add(audit)
        
        # Eliminar plan
        db.delete(plan)
        db.commit()
        
        return True
    
    @staticmethod
    def get_plan_with_stats(
        db: Session,
        plan_id: str,
        current_user: User
    ) -> dict:
        """
        Obtiene un plan con estadísticas de comidas
        
        Args:
            db: Sesión de base de datos
            plan_id: ID del plan
            current_user: Usuario autenticado
        
        Returns:
            Diccionario con plan y estadísticas
        """
        plan = NutritionPlanController.get_by_id(db, plan_id, current_user)
        
        # Obtener estadísticas de comidas
        meal_stats = db.query(
            func.count(Meal.id).label('total_meals'),
            func.avg(Meal.calories).label('avg_calories')
        ).filter(
            Meal.plan_id == plan.id
        ).first()
        
        return {
            "id": str(plan.id),
            "pet_id": str(plan.pet_id),
            "name": plan.name,
            "description": plan.description,
            "calories_per_day": plan.calories_per_day,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat(),
            "total_meals": meal_stats.total_meals or 0,
            "average_calories_per_meal": float(meal_stats.avg_calories) if meal_stats.avg_calories else None
        }
    
    @staticmethod
    def get_active_plan_for_pet(
        db: Session,
        pet_id: str,
        current_user: User
    ) -> Optional[NutritionPlan]:
        """
        Obtiene el plan de nutrición activo para una mascota
        (el más reciente)
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            current_user: Usuario autenticado
        
        Returns:
            Plan de nutrición más reciente o None
        """
        # Verificar que la mascota pertenece al usuario
        pet = db.query(Pet).filter(
            Pet.id == pet_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )
        
        # Obtener el plan más reciente
        plan = db.query(NutritionPlan).filter(
            NutritionPlan.pet_id == pet_id
        ).order_by(desc(NutritionPlan.created_at)).first()
        
        return plan
    
    @staticmethod
    def duplicate_plan(
        db: Session,
        plan_id: str,
        new_pet_id: Optional[str],
        current_user: User
    ) -> NutritionPlan:
        """
        Duplica un plan de nutrición existente
        
        Args:
            db: Sesión de base de datos
            plan_id: ID del plan a duplicar
            new_pet_id: ID de la nueva mascota (opcional, usa la misma si no se proporciona)
            current_user: Usuario autenticado
        
        Returns:
            Nuevo plan duplicado
        """
        original_plan = NutritionPlanController.get_by_id(db, plan_id, current_user)
        
        # Determinar pet_id para el nuevo plan
        target_pet_id = new_pet_id if new_pet_id else original_plan.pet_id
        
        # Verificar que la mascota existe
        pet = db.query(Pet).filter(
            Pet.id == target_pet_id,
            Pet.owner_id == current_user.id
        ).first()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota de destino no encontrada"
            )
        
        # Crear plan duplicado
        new_plan = NutritionPlan(
            pet_id=target_pet_id,
            name=f"{original_plan.name} (copia)",
            description=original_plan.description,
            calories_per_day=original_plan.calories_per_day
        )
        
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        
        # Log de auditoría
        audit = AuditLog(
            actor_user_id=current_user.id,
            action="NUTRITION_PLAN_DUPLICATED",
            object_type="NutritionPlan",
            object_id=new_plan.id,
            meta={
                "original_plan_id": str(original_plan.id),
                "new_plan_name": new_plan.name,
                "pet_id": str(target_pet_id)
            }
        )
        db.add(audit)
        db.commit()
        
        return new_plan