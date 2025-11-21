-- ========================================
-- Script SQL COMBINADO para cambios en pet_photos
-- ========================================
-- Este script aplica TODOS los cambios necesarios en la tabla pet_photos:
-- 1. Agrega campo is_profile (BOOLEAN)
-- 2. Elimina campo data (BYTEA) - no se usa
-- 
-- IMPORTANTE: Si ejecutas este script SQL directamente, NO ejecutes las migraciones
-- de Alembic, ya que causarían conflictos. Las migraciones están solo como referencia.
-- 
-- Ejecutar en PostgreSQL:
-- Local: psql -U petuser -d pet_health_tracker -f apply_pet_photos_changes.sql
-- Render: Conectarse a la BD y ejecutar este script

-- Conectar al schema correcto
SET search_path TO petcare;

-- ========================================
-- PASO 1: Agregar campo is_profile
-- ========================================
DO $$
BEGIN
    -- Verificar si la columna ya existe
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'petcare' 
          AND table_name = 'pet_photos' 
          AND column_name = 'is_profile'
    ) THEN
        -- Agregar columna is_profile con valor por defecto FALSE
        ALTER TABLE pet_photos 
        ADD COLUMN is_profile BOOLEAN NOT NULL DEFAULT FALSE;
        
        -- Crear índice compuesto para mejorar búsquedas de fotos de perfil
        CREATE INDEX idx_pet_photos_is_profile 
        ON pet_photos(pet_id, is_profile);
        
        -- Comentario en la columna para documentación
        COMMENT ON COLUMN pet_photos.is_profile IS 
        'Indica si la foto es de perfil (true) o de galería (false). Solo puede haber una foto de perfil por mascota.';
        
        RAISE NOTICE '✅ Campo is_profile agregado exitosamente';
    ELSE
        RAISE NOTICE '⚠️ Campo is_profile ya existe, omitiendo...';
    END IF;
END $$;

-- ========================================
-- PASO 2: Eliminar campo data
-- ========================================
DO $$
BEGIN
    -- Verificar si la columna existe antes de eliminarla
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'petcare' 
          AND table_name = 'pet_photos' 
          AND column_name = 'data'
    ) THEN
        -- Eliminar columna data
        ALTER TABLE pet_photos DROP COLUMN data;
        RAISE NOTICE '✅ Columna data eliminada exitosamente';
    ELSE
        RAISE NOTICE '⚠️ La columna data no existe, omitiendo...';
    END IF;
END $$;

-- ========================================
-- VERIFICACIÓN FINAL
-- ========================================
SELECT 
    column_name, 
    data_type, 
    column_default, 
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'petcare' 
  AND table_name = 'pet_photos'
ORDER BY ordinal_position;

-- Mensaje de éxito
SELECT '✅ Todos los cambios aplicados exitosamente en pet_photos' AS resultado;

