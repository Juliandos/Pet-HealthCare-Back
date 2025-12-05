-- ========================================
-- Script para actualizar restricciones CASCADE en la base de datos
-- Ejecutar este script en PostgreSQL para asegurar que todas las relaciones
-- tengan eliminación en cascada cuando se borre una mascota
-- ========================================

-- IMPORTANTE: Hacer backup de la base de datos antes de ejecutar este script

BEGIN;

-- 1. Eliminar y recrear restricción de pet_photos -> pets
ALTER TABLE petcare.pet_photos 
DROP CONSTRAINT IF EXISTS pet_photos_pet_id_fkey;

ALTER TABLE petcare.pet_photos 
ADD CONSTRAINT pet_photos_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 2. Eliminar y recrear restricción de vaccinations -> pets
ALTER TABLE petcare.vaccinations 
DROP CONSTRAINT IF EXISTS vaccinations_pet_id_fkey;

ALTER TABLE petcare.vaccinations 
ADD CONSTRAINT vaccinations_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 3. Eliminar y recrear restricción de dewormings -> pets
ALTER TABLE petcare.dewormings 
DROP CONSTRAINT IF EXISTS dewormings_pet_id_fkey;

ALTER TABLE petcare.dewormings 
ADD CONSTRAINT dewormings_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 4. Eliminar y recrear restricción de vet_visits -> pets
ALTER TABLE petcare.vet_visits 
DROP CONSTRAINT IF EXISTS vet_visits_pet_id_fkey;

ALTER TABLE petcare.vet_visits 
ADD CONSTRAINT vet_visits_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 5. Eliminar y recrear restricción de nutrition_plans -> pets
ALTER TABLE petcare.nutrition_plans 
DROP CONSTRAINT IF EXISTS nutrition_plans_pet_id_fkey;

ALTER TABLE petcare.nutrition_plans 
ADD CONSTRAINT nutrition_plans_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 6. Eliminar y recrear restricción de meals -> pets
ALTER TABLE petcare.meals 
DROP CONSTRAINT IF EXISTS meals_pet_id_fkey;

ALTER TABLE petcare.meals 
ADD CONSTRAINT meals_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 7. Eliminar y recrear restricción de reminders -> pets
ALTER TABLE petcare.reminders 
DROP CONSTRAINT IF EXISTS reminders_pet_id_fkey;

ALTER TABLE petcare.reminders 
ADD CONSTRAINT reminders_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 8. Eliminar y recrear restricción de notifications -> pets (cambiar de SET NULL a CASCADE)
ALTER TABLE petcare.notifications 
DROP CONSTRAINT IF EXISTS notifications_pet_id_fkey;

ALTER TABLE petcare.notifications 
ADD CONSTRAINT notifications_pet_id_fkey 
FOREIGN KEY (pet_id) 
REFERENCES petcare.pets(id) 
ON DELETE CASCADE;

-- 9. Limpiar registros corruptos (registros con pet_id null donde no debería ser null)
-- Esto elimina registros huérfanos que pueden causar problemas

-- Eliminar vacunaciones con pet_id null
DELETE FROM petcare.vaccinations WHERE pet_id IS NULL;

-- Eliminar desparasitaciones con pet_id null
DELETE FROM petcare.dewormings WHERE pet_id IS NULL;

-- Eliminar visitas veterinarias con pet_id null
DELETE FROM petcare.vet_visits WHERE pet_id IS NULL;

-- Eliminar comidas con pet_id null
DELETE FROM petcare.meals WHERE pet_id IS NULL;

-- Eliminar planes de nutrición con pet_id null
DELETE FROM petcare.nutrition_plans WHERE pet_id IS NULL;

-- Eliminar recordatorios con pet_id null (opcional, ya que pet_id puede ser null en reminders)
-- DELETE FROM petcare.reminders WHERE pet_id IS NULL;

-- Eliminar notificaciones con pet_id null (ahora que cambiamos a CASCADE, estas se eliminarán automáticamente)
-- Pero podemos limpiar las existentes
DELETE FROM petcare.notifications WHERE pet_id IS NULL;

COMMIT;

-- Verificar que las restricciones se aplicaron correctamente
SELECT 
    tc.table_schema, 
    tc.table_name, 
    tc.constraint_name, 
    rc.delete_rule
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.referential_constraints AS rc 
        ON tc.constraint_name = rc.constraint_name
WHERE 
    tc.table_schema = 'petcare'
    AND tc.constraint_type = 'FOREIGN KEY'
    AND rc.unique_constraint_name IN (
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_schema = 'petcare' 
        AND table_name = 'pets' 
        AND constraint_type = 'PRIMARY KEY'
    )
ORDER BY tc.table_name, tc.constraint_name;

