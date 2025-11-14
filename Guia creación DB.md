# 🐾 Guía Actualizada de Configuración de Base de Datos – Pet HealthCare Back

## 📘 Descripción General

Este documento describe **exclusivamente** el proceso de **configuración y reinicio completo de la base de datos PostgreSQL** para el backend del proyecto **Pet HealthCare**.

> ⚠️ **Nota:** Esta guía cubre solo la configuración de la **base de datos**. Posteriormente se agregarán secciones para la configuración del servidor, dependencias, y FastAPI.

---

## 🧩 1. Entorno y Herramientas

* **Sistema operativo:** Ubuntu WSL (Windows 11)
* **Base de datos:** PostgreSQL 16
* **Usuario de BD:** `petuser`
* **Esquema:** `petcare`
* **Herramientas:** `psql`, `pgAdmin` (opcional)

---

## 🛠️ 2. Reinicio Completo de la Base de Datos

### 🔐 Conectarse como superusuario

```bash
sudo -u postgres psql
```

### 🔄 Eliminar conexiones activas y borrar la base existente

```sql
-- Cerrar conexiones activas
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE datname = 'pet_health_tracker';

-- Borrar la base de datos si existe
DROP DATABASE IF EXISTS pet_health_tracker;
```

### 🔒 Borrar usuario anterior (si existe)

```sql
DROP USER IF EXISTS petuser;
```

### 🔧 Crear usuario, base de datos y esquema

```sql
-- Crear usuario con contraseña
CREATE USER petuser WITH PASSWORD 'pet_user_no_country';

-- Crear base de datos con el nuevo usuario como propietario
CREATE DATABASE pet_health_tracker OWNER petuser;

-- Conectarse a la base recién creada
\c pet_health_tracker

-- Crear esquema principal
CREATE SCHEMA petcare AUTHORIZATION petuser;
```

### 🔑 Otorgar permisos completos

```sql
-- Privilegios sobre la base de datos
GRANT ALL PRIVILEGES ON DATABASE pet_health_tracker TO petuser;

-- Permisos sobre el esquema
GRANT ALL PRIVILEGES ON SCHEMA petcare TO petuser;

-- Permisos sobre tablas y secuencias existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA petcare TO petuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA petcare TO petuser;

-- Privilegios por defecto para futuros objetos
ALTER DEFAULT PRIVILEGES IN SCHEMA petcare GRANT ALL ON TABLES TO petuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA petcare GRANT ALL ON SEQUENCES TO petuser;

-- Permitir creación de objetos dentro del esquema
GRANT CREATE, USAGE ON SCHEMA petcare TO petuser;
```

---

## 🗞️ 3. Archivo `.env`

**Ruta:**
`/mnt/c/Users/ASUS/Desktop/rescate asus/Yo/Paginas Web/Propio/Pet-HealthCare-Back/.env`

**Contenido:**

```env
DATABASE_URL=postgresql+psycopg2://petuser:pet_user_no_country@localhost/pet_health_tracker
```

---

## 🖊️ 4. (Opcional) Cargar el Esquema de Tablas

Si ya tienes el archivo SQL del esquema (`pet_health_tracker_schema.sql`):

```bash
psql -U postgres -d pet_health_tracker -f pet_health_tracker_schema.sql
```

Esto creará todas las tablas del esquema `petcare` (como `users`, `pets`, `notifications`, etc.).

---

## 🔎 5. Verificación de la Configuración

Conectarse como `petuser`:

```bash
psql -U petuser -h localhost -d pet_health_tracker
```

Dentro de `psql`:

```sql
\dn               -- listar esquemas
\dt petcare.*     -- listar tablas
CREATE TABLE petcare.test_table(id SERIAL PRIMARY KEY);
DROP TABLE petcare.test_table;
```

Si no se presentan errores, el usuario `petuser` tiene control total sobre el esquema `petcare` y la base.

---

## 🔍 Estado Actual

| Elemento                                    | Estado |
| ------------------------------------------- | ------ |
| PostgreSQL instalado                        | ✅      |
| Base de datos creada (`pet_health_tracker`) | ✅      |
| Usuario `petuser` creado                    | ✅      |
| Permisos otorgados                          | ✅      |
| Esquema `petcare` configurado               | ✅      |
| Archivo `.env` configurado                  | ✅      |

---

## 🚀 Próximos Pasos (fuera del alcance de esta guía)

* Configurar **FastAPI** y **SQLAlchemy** para conectarse a `DATABASE_URL`.
* Configurar **Alembic** para migraciones automáticas.
* Crear modelos ORM (`models.py`) y CRUDs (`crud.py`).
* Definir endpoints REST con autenticación y validación.

---

📝 **Autor:** Julian Ortega
🗓 **Actualizado:** {{fecha_actual}}
