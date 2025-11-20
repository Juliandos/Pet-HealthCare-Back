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
            # Corregir password_resets
            "ALTER TABLE petcare.password_resets DROP CONSTRAINT IF EXISTS password_resets_user_id_fkey;",
            """ALTER TABLE petcare.password_resets
               ADD CONSTRAINT password_resets_user_id_fkey 
               FOREIGN KEY (user_id) 
               REFERENCES petcare.users(id) 
               ON DELETE CASCADE;""",
            
            # Corregir audit_logs
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

