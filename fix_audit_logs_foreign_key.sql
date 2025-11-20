-- =============================================
-- Script SQL para corregir la foreign key de audit_logs
-- Permite eliminar usuarios sin error de llaves foráneas
-- =============================================

-- Eliminar la constraint existente
ALTER TABLE petcare.audit_logs 
DROP CONSTRAINT IF EXISTS audit_logs_actor_user_id_fkey;

-- Crear la nueva constraint con ON DELETE SET NULL
ALTER TABLE petcare.audit_logs
ADD CONSTRAINT audit_logs_actor_user_id_fkey 
FOREIGN KEY (actor_user_id) 
REFERENCES petcare.users(id) 
ON DELETE SET NULL;

-- Verificar que se aplicó correctamente
SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'petcare.audit_logs'::regclass
AND conname = 'audit_logs_actor_user_id_fkey';

