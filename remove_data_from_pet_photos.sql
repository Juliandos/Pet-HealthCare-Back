-- ========================================
-- Script SQL para eliminar campo data de pet_photos
-- ========================================
-- Este script elimina el campo data (BYTEA) de la tabla pet_photos
-- ya que no se está usando. Las imágenes se almacenan en S3 y solo
-- guardamos la URL en la base de datos.
-- 
-- Ejecutar en PostgreSQL:
-- psql -U usuario -d nombre_db -f remove_data_from_pet_photos.sql

-- Conectar al schema correcto
SET search_path TO petcare;

-- 1. Verificar que la columna existe antes de eliminarla
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'petcare' 
          AND table_name = 'pet_photos' 
          AND column_name = 'data'
    ) THEN
        -- Eliminar columna data
        ALTER TABLE pet_photos DROP COLUMN data;
        RAISE NOTICE '✅ Columna data eliminada exitosamente de pet_photos';
    ELSE
        RAISE NOTICE '⚠️ La columna data no existe en pet_photos';
    END IF;
END $$;

-- 2. Verificar que se eliminó correctamente
SELECT 
    column_name, 
    data_type
FROM information_schema.columns
WHERE table_schema = 'petcare' 
  AND table_name = 'pet_photos'
ORDER BY ordinal_position;

-- Mensaje de éxito
SELECT '✅ Campo data eliminado exitosamente de pet_photos' AS resultado;

