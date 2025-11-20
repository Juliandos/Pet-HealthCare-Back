-- =============================================
-- Script SQL para corregir las foreign keys y permitir eliminar usuarios
-- Corrige audit_logs y password_resets
-- =============================================

-- 1. Corregir audit_logs: permitir NULL cuando se elimina el usuario
ALTER TABLE petcare.audit_logs 
DROP CONSTRAINT IF EXISTS audit_logs_actor_user_id_fkey;

ALTER TABLE petcare.audit_logs
ADD CONSTRAINT audit_logs_actor_user_id_fkey 
FOREIGN KEY (actor_user_id) 
REFERENCES petcare.users(id) 
ON DELETE SET NULL;

-- 2. Corregir password_resets: eliminar en cascada cuando se elimina el usuario
ALTER TABLE petcare.password_resets 
DROP CONSTRAINT IF EXISTS password_resets_user_id_fkey;

ALTER TABLE petcare.password_resets
ADD CONSTRAINT password_resets_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES petcare.users(id) 
ON DELETE CASCADE;

-- 3. Verificar que se aplicaron correctamente
SELECT 
    conrelid::regclass AS tabla,
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid IN ('petcare.audit_logs'::regclass, 'petcare.password_resets'::regclass)
AND conname IN ('audit_logs_actor_user_id_fkey', 'password_resets_user_id_fkey')
ORDER BY conrelid;

