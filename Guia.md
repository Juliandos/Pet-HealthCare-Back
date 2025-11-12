# 🐾 Guía de Configuración de Base de Datos – Pet HealthCare Back

## 📘 Descripción General
Este documento resume el proceso de configuración de la base de datos PostgreSQL utilizada por el backend del proyecto **Pet HealthCare** desarrollado con **FastAPI** y **SQLAlchemy**.

La base de datos se ejecuta en **PostgreSQL** dentro de **Ubuntu WSL (Windows Subsystem for Linux)**.

---

## 🧩 1. Entorno y Herramientas

- **Sistema operativo:** Ubuntu WSL (Windows 11)
- **Gestor de versiones de Python:** `pyenv`
- **Entorno virtual:** `venv`
- **Base de datos:** PostgreSQL 16
- **ORM:** SQLAlchemy (vinculado con FastAPI)
- **Migraciones:** Alembic

---

## ⚙️ 2. Creación del Proyecto Backend

Ruta del proyecto:
/mnt/c/Users/ASUS/Desktop/rescate asus/Yo/Paginas Web/Propio/Pet-HealthCare-Back

bash
Copiar código

Creación del entorno y dependencias:
```bash
python -m venv venv
source venv/bin/activate
pip install "fastapi" "uvicorn" "sqlalchemy" "psycopg2-binary" "python-dotenv" "alembic"
🐘 3. Configuración de PostgreSQL
Ver usuarios existentes
sql
Copiar código
\du
Ver bases de datos existentes
sql
Copiar código
\l
🧱 4. Creación de la Base de Datos y Usuario
Conéctate como superusuario:

bash
Copiar código
psql -U postgres
Luego ejecuta:

sql
Copiar código
CREATE USER petuser WITH PASSWORD 'pet_user_no_country';
CREATE DATABASE pet_health_tracker OWNER petuser;
GRANT ALL PRIVILEGES ON DATABASE pet_health_tracker TO petuser;
🧩 5. Cargar el Esquema de la Base de Datos
Archivo SQL:
pet_health_tracker_schema.sql

Ruta:

swift
Copiar código
/mnt/c/Users/ASUS/Desktop/rescate asus/Yo/Paginas Web/Propio/Pet-HealthCare-Back/pet_health_tracker_schema.sql
Ejecutar:

bash
Copiar código
psql -U postgres -d pet_health_tracker -f pet_health_tracker_schema.sql
✅ Este archivo crea el esquema petcare y todas las tablas:

users, pets, pet_photos, vaccinations, dewormings,
vet_visits, nutrition_plans, meals, reminders, notifications,
password_resets, audit_logs, entre otras.

🔐 6. Otorgar Permisos Completos al Usuario petuser
Conéctate nuevamente como postgres:

bash
Copiar código
psql -U postgres -d pet_health_tracker
Y ejecuta:

sql
Copiar código
-- Privilegios sobre la DB
GRANT ALL PRIVILEGES ON DATABASE pet_health_tracker TO petuser;

-- Privilegios sobre el esquema
GRANT ALL PRIVILEGES ON SCHEMA petcare TO petuser;

-- Privilegios sobre tablas y secuencias existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA petcare TO petuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA petcare TO petuser;

-- Privilegios por defecto para futuros objetos
ALTER DEFAULT PRIVILEGES IN SCHEMA petcare
GRANT ALL ON TABLES TO petuser;

ALTER DEFAULT PRIVILEGES IN SCHEMA petcare
GRANT ALL ON SEQUENCES TO petuser;

-- Permitir creación de objetos dentro del esquema
GRANT CREATE, USAGE ON SCHEMA petcare TO petuser;
🧾 7. Crear Archivo .env
Ruta:
/mnt/c/Users/ASUS/Desktop/rescate asus/Yo/Paginas Web/Propio/Pet-HealthCare-Back/.env

Contenido:

env
Copiar código
DATABASE_URL=postgresql+psycopg2://petuser:pet_user_no_country@localhost/pet_health_tracker
🧠 8. Verificación de Conexión
Conectarse como petuser:

bash
Copiar código
psql -U petuser -h localhost -d pet_health_tracker
Comprobar acceso:

sql
Copiar código
\dn              -- listar esquemas
\dt petcare.*    -- listar tablas del esquema
CREATE TABLE petcare.test_table(id SERIAL PRIMARY KEY);  -- prueba
DROP TABLE petcare.test_table;
Si todo funciona correctamente, el usuario tiene control total sobre el esquema y la base.

✅ Estado Actual
Elemento	Estado
PostgreSQL instalado	✅
Base de datos creada (pet_health_tracker)	✅
Usuario petuser creado	✅
Permisos otorgados	✅
Esquema petcare cargado con todas las tablas	✅
Archivo .env configurado	✅

🚀 Próximos Pasos
Conectar SQLAlchemy al DATABASE_URL desde FastAPI.

Configurar Alembic para migraciones.

Crear los modelos ORM (models.py).

Crear controladores CRUD (crud.py) y endpoints (routers/).

📄 Autor: Julian Ortega
🗓️ Última actualización: {{fecha_actual}}