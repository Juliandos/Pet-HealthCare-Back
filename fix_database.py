#!/usr/bin/env python3
"""
Script para corregir las foreign keys directamente desde Python
Ejecutar en Render Shell: python fix_database.py
"""
import os
from sqlalchemy import create_engine, text

# Obtener la URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL no está configurada")
    exit(1)

print(f"🔗 Conectando a la base de datos...")

# Crear conexión
engine = create_engine(DATABASE_URL)

# SQL a ejecutar
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

try:
    with engine.connect() as conn:
        for i, sql in enumerate(sql_statements, 1):
            print(f"📝 Ejecutando statement {i}/{len(sql_statements)}...")
            conn.execute(text(sql))
            conn.commit()
            print(f"✅ Statement {i} ejecutado")
        
        # Verificar
        print("\n🔍 Verificando constraints...")
        result = conn.execute(text("""
            SELECT 
                conrelid::regclass AS tabla,
                conname AS constraint_name,
                pg_get_constraintdef(oid) AS definition
            FROM pg_constraint
            WHERE conrelid IN ('petcare.audit_logs'::regclass, 'petcare.password_resets'::regclass)
            AND conname IN ('audit_logs_actor_user_id_fkey', 'password_resets_user_id_fkey')
            ORDER BY conrelid;
        """))
        
        print("\n📋 Constraints actualizadas:")
        for row in result:
            print(f"  ✅ {row.tabla}.{row.constraint_name}")
            print(f"     {row.definition}")
        
        print("\n✅ ¡Base de datos corregida exitosamente!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)