# 📋 Instrucciones para Aplicar Cambios en pet_photos

## ⚠️ IMPORTANTE: Migraciones vs SQL Directo

**Si ejecutas los scripts SQL directamente (como vamos a hacer), NO ejecutes las migraciones de Alembic.**

Las migraciones de Alembic están solo como referencia/documentación. Si ejecutas ambas cosas, causarías conflictos.

---

## 🎯 Opción Recomendada: SQL Directo

### ✅ Ventajas:
- Funciona en Render (donde Alembic a veces falla)
- Control total sobre qué se ejecuta
- Más rápido y directo
- No depende de la configuración de Alembic

### 📝 Pasos:

---

## 📍 PASO 1: Aplicar en Base de Datos LOCAL

### En Linux (WSL o Linux nativo):

```bash
# Conectarse a PostgreSQL
psql -U petuser -d pet_health_tracker

# O si necesitas especificar host:
psql -h localhost -U petuser -d pet_health_tracker

# Una vez conectado, ejecutar:
\c pet_health_tracker
SET search_path TO petcare;

# Copiar y pegar el contenido de apply_pet_photos_changes.sql
# O ejecutar directamente:
\i apply_pet_photos_changes.sql
```

### O desde la línea de comandos directamente:

```bash
psql -U petuser -d pet_health_tracker -f apply_pet_photos_changes.sql
```

---

## 📍 PASO 2: Aplicar en Base de Datos RENDER

### Opción A: Desde el Dashboard de Render

1. Ve a tu servicio de base de datos en Render
2. Haz clic en "Connect" o "Shell"
3. Abre la conexión a PostgreSQL
4. Copia y pega el contenido completo de `apply_pet_photos_changes.sql`
5. Ejecuta el script

### Opción B: Desde psql local conectado a Render

```bash
# Obtener la cadena de conexión de Render
# Formato: postgresql://usuario:password@host:puerto/database

psql "postgresql://usuario:password@host:puerto/database" -f apply_pet_photos_changes.sql
```

### Opción C: Desde pgAdmin o DBeaver

1. Conecta a tu base de datos de Render
2. Abre el editor SQL
3. Copia y pega el contenido de `apply_pet_photos_changes.sql`
4. Ejecuta el script

---

## ✅ Verificación

Después de ejecutar el script, deberías ver:

```sql
-- Verificar estructura de la tabla
SELECT 
    column_name, 
    data_type, 
    column_default, 
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'petcare' 
  AND table_name = 'pet_photos'
ORDER BY ordinal_position;
```

**Resultado esperado:**
- ✅ `is_profile` (BOOLEAN, default FALSE) - DEBE estar
- ❌ `data` (BYTEA) - NO debe estar

---

## 🔄 ¿Qué hacer con las Migraciones de Alembic?

### Opción 1: Ignorarlas (Recomendado si siempre usas SQL directo)
- Simplemente no ejecutes `alembic upgrade head`
- Las migraciones quedan como documentación
- Alembic seguirá funcionando para futuras migraciones

### Opción 2: Marcar como ejecutadas (Si quieres mantener Alembic sincronizado)

Si quieres que Alembic sepa que estos cambios ya están aplicados:

```bash
# Marcar las migraciones como ejecutadas sin ejecutarlas
alembic stamp add_is_profile_pet_photos
alembic stamp remove_data_pet_photos
```

Esto actualiza la tabla `alembic_version` sin ejecutar las migraciones.

---

## 📁 Archivos Involucrados

- ✅ **`apply_pet_photos_changes.sql`** - Script SQL combinado (USAR ESTE)
- 📄 `add_is_profile_to_pet_photos.sql` - Solo agrega is_profile (opcional)
- 📄 `remove_data_from_pet_photos.sql` - Solo elimina data (opcional)
- 📄 `alembic/versions/add_is_profile_to_pet_photos.py` - Migración (solo referencia)
- 📄 `alembic/versions/remove_data_from_pet_photos.py` - Migración (solo referencia)

---

## 🚨 Si algo sale mal

### Rollback (revertir cambios):

```sql
-- Revertir: Eliminar is_profile
ALTER TABLE petcare.pet_photos DROP COLUMN IF EXISTS is_profile;
DROP INDEX IF EXISTS petcare.idx_pet_photos_is_profile;

-- Revertir: Agregar data de vuelta
ALTER TABLE petcare.pet_photos ADD COLUMN IF NOT EXISTS data BYTEA;
```

---

## ✅ Checklist Final

- [ ] Ejecuté el script SQL en la base de datos LOCAL
- [ ] Verifiqué que los cambios se aplicaron correctamente en LOCAL
- [ ] Ejecuté el script SQL en la base de datos de RENDER
- [ ] Verifiqué que los cambios se aplicaron correctamente en RENDER
- [ ] El código Python ya está actualizado (modelo y controlador)
- [ ] NO ejecuté las migraciones de Alembic (para evitar conflictos)

---

## 💡 Nota Final

**¿Por qué SQL directo en lugar de migraciones?**

- Render a veces tiene problemas con Alembic durante el build
- SQL directo es más confiable y predecible
- Tienes control total sobre cuándo y cómo se ejecutan los cambios
- Las migraciones quedan como documentación de los cambios realizados

