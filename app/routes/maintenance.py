"""
Endpoint temporal para mantenimiento de base de datos
ELIMINAR DESPUÉS DE USAR
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.middleware.auth import get_db, require_role
from app.models import User

router = APIRouter(prefix="/maintenance", tags=["Mantenimiento"])

@router.post("/force-delete-corrupt-record")
def force_delete_corrupt_record(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    🔨 Elimina FORZADAMENTE el registro corrupto específico
    ⚠️ Solo accesible por administradores
    """
    try:
        # El ID problemático que vemos en los logs
        corrupt_id = "35452231-6dfb-433c-8910-f094c53f4728"
        
        # Verificar si existe
        check = db.execute(text("""
            SELECT id, user_id, token, created_at
            FROM petcare.password_resets
            WHERE id = :record_id;
        """), {"record_id": corrupt_id})
        
        record = check.fetchone()
        
        if record:
            # Eliminar por ID específico
            db.execute(text("DELETE FROM petcare.password_resets WHERE id = :record_id;"), {"record_id": corrupt_id})
            db.commit()
            
            return {
                "success": True,
                "message": f"✅ Registro corrupto {corrupt_id} eliminado",
                "deleted_record": {
                    "id": str(record.id),
                    "user_id": record.user_id,
                    "token": record.token,
                    "created_at": str(record.created_at)
                }
            }
        else:
            return {
                "success": True,
                "message": "✅ El registro corrupto ya no existe",
                "deleted_record": None
            }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar registro corrupto: {str(e)}"
        )

@router.post("/fix-foreign-keys")
def fix_foreign_keys(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    🔧 Endpoint temporal para corregir foreign keys
    ⚠️ Solo accesible por administradores
    🗑️ ELIMINAR DESPUÉS DE USAR
    """
    try:
        sql_statements = [
            # Primero: Limpiar registros corruptos con user_id NULL
            "DELETE FROM petcare.password_resets WHERE user_id IS NULL;",
            
            # Segundo: Corregir password_resets
            "ALTER TABLE petcare.password_resets DROP CONSTRAINT IF EXISTS password_resets_user_id_fkey;",
            """ALTER TABLE petcare.password_resets
               ADD CONSTRAINT password_resets_user_id_fkey 
               FOREIGN KEY (user_id) 
               REFERENCES petcare.users(id) 
               ON DELETE CASCADE;""",
            
            # Tercero: Corregir audit_logs (permitir NULL aquí es correcto)
            "ALTER TABLE petcare.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_actor_user_id_fkey;",
            """ALTER TABLE petcare.audit_logs
               ADD CONSTRAINT audit_logs_actor_user_id_fkey 
               FOREIGN KEY (actor_user_id) 
               REFERENCES petcare.users(id) 
               ON DELETE SET NULL;""",
        ]
        
        results = []
        for i, sql in enumerate(sql_statements, 1):
            db.execute(text(sql))
            db.commit()
            results.append(f"✅ Statement {i}/{len(sql_statements)} ejecutado")
        
        # Verificar
        verification = db.execute(text("""
            SELECT 
                conrelid::regclass AS tabla,
                conname AS constraint_name,
                pg_get_constraintdef(oid) AS definition
            FROM pg_constraint
            WHERE conrelid IN ('petcare.audit_logs'::regclass, 'petcare.password_resets'::regclass)
            AND conname IN ('audit_logs_actor_user_id_fkey', 'password_resets_user_id_fkey')
            ORDER BY conrelid;
        """))
        
        constraints = []
        for row in verification:
            constraints.append({
                "tabla": str(row.tabla),
                "constraint": row.constraint_name,
                "definition": row.definition
            })
        
        return {
            "success": True,
            "message": "✅ Foreign keys corregidas exitosamente",
            "executed_statements": results,
            "constraints": constraints
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al corregir foreign keys: {str(e)}"
        )

