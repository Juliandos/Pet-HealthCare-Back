-- ========================================
-- Script SQL para agregar campo is_profile a pet_photos
-- ========================================
-- Este script agrega el campo is_profile (BOOLEAN) a la tabla pet_photos
-- para distinguir entre fotos de perfil y fotos de galería.
-- 
-- IMPORTANTE: Solo puede haber UNA foto de perfil (is_profile=true) por mascota.
-- 
-- Ejecutar en PostgreSQL:
-- psql -U usuario -d nombre_db -f add_is_profile_to_pet_photos.sql

-- Conectar al schema correcto
SET search_path TO petcare;

-- 1. Agregar columna is_profile con valor por defecto FALSE
ALTER TABLE pet_photos 
ADD COLUMN IF NOT EXISTS is_profile BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Crear índice compuesto para mejorar búsquedas de fotos de perfil
CREATE INDEX IF NOT EXISTS idx_pet_photos_is_profile 
ON pet_photos(pet_id, is_profile);

-- 3. Comentario en la columna para documentación
COMMENT ON COLUMN pet_photos.is_profile IS 
'Indica si la foto es de perfil (true) o de galería (false). Solo puede haber una foto de perfil por mascota.';

-- 4. Verificar que se agregó correctamente
SELECT 
    column_name, 
    data_type, 
    column_default, 
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'petcare' 
  AND table_name = 'pet_photos' 
  AND column_name = 'is_profile';

-- Mensaje de éxito
SELECT '✅ Campo is_profile agregado exitosamente a pet_photos' AS resultado;

