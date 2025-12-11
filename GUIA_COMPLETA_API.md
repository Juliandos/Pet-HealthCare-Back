# 🐾 Guía Completa: Pet HealthCare API

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Instalación y Configuración](#instalación-y-configuración)
3. [Autenticación](#autenticación)
4. [Endpoints de la API](#endpoints-de-la-api)
5. [Chat IA Veterinario](#chat-ia-veterinario)
6. [Solución de Problemas](#solución-de-problemas)

---

## 📘 Descripción General

**Pet HealthCare API** es una API REST completa para la gestión de salud de mascotas que incluye:

- ✅ Gestión completa de usuarios y autenticación JWT
- ✅ CRUD completo de mascotas
- ✅ Registro de vacunaciones, desparasitaciones y visitas veterinarias
- ✅ Planes de nutrición y registro de comidas
- ✅ Sistema de recordatorios y notificaciones
- ✅ Gestión de imágenes y documentos (S3)
- ✅ **Chat con IA Veterinario** usando LangChain y OpenAI
- ✅ Análisis de documentos PDF con RAG (Retrieval Augmented Generation)

**URL Base de Producción:** `https://pet-healthcare-back.onrender.com`

**Documentación Interactiva:**
- Swagger UI: `https://pet-healthcare-back.onrender.com/docs`
- ReDoc: `https://pet-healthcare-back.onrender.com/redoc`

---

## 🔧 Instalación y Configuración

### 📋 Requisitos Previos

- Python 3.11+
- PostgreSQL 12+ (local o en Render)
- Cuentas creadas:
  - OpenAI (para API key): https://platform.openai.com/api-keys
  - LangSmith (opcional, para monitoreo): https://smith.langchain.com/
  - AWS S3 (para almacenamiento de imágenes y documentos)

---

### 🗄️ PARTE 1: Instalar pgvector en PostgreSQL

La extensión pgvector permite almacenar vectores (embeddings) en PostgreSQL para el sistema de Chat IA.

#### 🖥️ Para Desarrollo Local (Ubuntu)

```bash
# 1. Actualizar paquetes
sudo apt update

# 2. Instalar dependencias
# Nota: Reemplaza "16" con tu versión de PostgreSQL (verifica con: psql --version)
sudo apt install -y postgresql-server-dev-16 build-essential git

# 3. Clonar pgvector en carpeta temporal
cd /tmp
git clone --branch v0.4.1 https://github.com/pgvector/pgvector.git
cd pgvector

# 4. Compilar e instalar
make
sudo make install

# 5. Crear extensión en PostgreSQL
sudo -u postgres psql -d pet_health_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 6. Verificar instalación
sudo -u postgres psql -d pet_health_tracker -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

#### ☁️ Para Producción en Render

**Método 1: Usando Render CLI (Recomendado)**
```bash
# Conectarte a la base de datos
render psql dpg-d4b3bnvgi27c7394445g-a

# En la consola de PostgreSQL, ejecutar:
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Método 2: Usando psql directamente**
```bash
# Conectarte usando la URL externa de Render
psql postgresql://pet_health_tracker_user:Qee0581vKSojU9hTVqHc0v5QY9R3hOZX@dpg-d4b3bnvgi27c7394445g-a.oregon-postgres.render.com/pet_health_tracker

# En la consola de PostgreSQL, ejecutar:
CREATE EXTENSION IF NOT EXISTS vector;
```

**Método 3: Desde el Dashboard de Render**
1. Ve al dashboard de Render
2. Selecciona tu base de datos PostgreSQL (`pet_health_tracker`)
3. Ve a "Connect" → "Connect via psql"
4. Ejecuta: `CREATE EXTENSION IF NOT EXISTS vector;`

---

### 📦 PARTE 2: Instalar Dependencias de Python

#### 🖥️ Para Desarrollo Local

```bash
# 1. Navegar al directorio del proyecto
cd /ruta/a/Pet-HealthCare-Back

# 2. Activar entorno virtual (si usas uno)
source venv/bin/activate

# 3. Actualizar pip
pip install --upgrade pip

# 4. Instalar todas las dependencias
pip install -r requirements.txt
```

#### ☁️ Para Producción en Render

Render instalará automáticamente las dependencias desde `requirements.txt` durante el deploy.

---

### 🔐 PARTE 3: Configurar Variables de Entorno

#### 🖥️ Para Desarrollo Local

Edita tu archivo `.env` en la raíz del proyecto:

```env
# ============================================
# BASE DE DATOS
# ============================================
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/pet_health_tracker

# ============================================
# SEGURIDAD
# ============================================
SECRET_KEY=tu-secret-key-super-segura
JWT_SECRET_KEY=tu-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ============================================
# AWS S3 (para imágenes y documentos)
# ============================================
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=pet-healthcare-images

# ============================================
# OPENAI (OBLIGATORIO para Chat IA)
# ============================================
# Obtén tu API key en: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-tu-api-key-aqui

# Modelo de OpenAI (opcional, por defecto: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Modelo de embeddings (opcional, por defecto: text-embedding-3-small)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Temperatura (0.0 = determinista, 1.0 = creativo)
OPENAI_TEMPERATURE=0.0

# ============================================
# LANGSMITH (OPCIONAL - Recomendado para desarrollo)
# ============================================
# Obtén tu API key en: https://smith.langchain.com/
LANGSMITH_API_KEY=ls-tu-api-key-aqui
LANGSMITH_PROJECT=pet-healthcare
LANGSMITH_TRACING=false  # true en desarrollo, false en producción

# ============================================
# RAG (OPCIONAL - valores por defecto)
# ============================================
RAG_CHUNK_SIZE=1000      # Tamaño de chunks (500-2000 recomendado)
RAG_CHUNK_OVERLAP=200    # Overlap entre chunks (100-300 recomendado)
RAG_TOP_K_RESULTS=4      # Documentos a recuperar (3-5 recomendado)

# ============================================
# EMAIL (OPCIONAL - para notificaciones)
# ============================================
RESEND_API_KEY=tu-resend-api-key
EMAIL_FROM=noreply@pethealthcare.com
```

#### ☁️ Para Producción en Render

1. Ve al dashboard de Render
2. Selecciona tu servicio (Web Service)
3. Ve a "Environment" → "Environment Variables"
4. Agrega todas las variables necesarias (sin comentarios)

**⚠️ Importante en Render:**
- `DATABASE_URL` ya debería estar configurada automáticamente
- No necesitas crear un archivo `.env` en Render
- Todas las variables se configuran en el dashboard

---

### 🧪 PARTE 4: Verificar Instalación

#### 🖥️ Local

```bash
# Verificar que pgvector está instalado
psql -U postgres -d pet_health_tracker -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Iniciar el servidor
uvicorn app.main:app --reload

# Verificar que el servidor está corriendo
# Deberías ver: "🚀 Pet HealthCare API v2.0 iniciada correctamente"
```

#### ☁️ Render

1. El servidor se inicia automáticamente después del deploy
2. Verifica los logs en el dashboard de Render
3. Visita: `https://pet-healthcare-back.onrender.com/docs`

---

## 🔐 Autenticación

La API usa **JWT (JSON Web Tokens)** para autenticación. La mayoría de los endpoints requieren autenticación.

### Flujo de Autenticación

1. **Registro/Login** → Obtener token JWT
2. **Usar token** → Incluir en header `Authorization: Bearer <token>`
3. **Token expira** → Usar refresh token o hacer login nuevamente

### Headers Requeridos

Para endpoints protegidos, incluye:

```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "Content-Type": "application/json"
}
```

---

## 🔗 Endpoints de la API

### 📍 Endpoints Generales

#### `GET /`
**Descripción:** Endpoint raíz que confirma que la API está funcionando

**Respuesta:**
```json
{
  "message": "🐾 Pet HealthCare API is running!",
  "version": "2.0.0",
  "docs": "/docs",
  "status": "online",
  "available_endpoints": {
    "auth": "/auth",
    "pets": "/pets",
    "vaccinations": "/vaccinations",
    "dewormings": "/dewormings",
    "vet_visits": "/vet-visits",
    "nutrition_plans": "/nutrition-plans",
    "meals": "/meals",
    "reminders": "/reminders",
    "notifications": "/notifications",
    "pet_photos": "/pet-photos",
    "chat": "/chat"
  }
}
```

#### `GET /health`
**Descripción:** Verifica el estado de salud de la API

**Respuesta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "2.0.0"
}
```

---

### 🔑 Autenticación (`/auth`)

#### `POST /auth/register`
**Descripción:** Registra un nuevo usuario en el sistema

**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "SecurePass123",
  "username": "usuario123",  // opcional
  "full_name": "Nombre Completo",  // opcional
  "phone": "+57 300 123 4567",  // opcional
  "timezone": "America/Bogota"  // opcional
}
```

**Respuesta:** `UserProfile` con datos del usuario creado

---

#### `POST /auth/login`
**Descripción:** Inicia sesión y obtiene tokens JWT

**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "SecurePass123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1440
}
```

---

#### `POST /auth/refresh`
**Descripción:** Renueva el access token usando el refresh token

**Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

#### `POST /auth/logout`
**Descripción:** Cierra sesión (invalida el refresh token)

**Headers:** Requiere autenticación

---

#### `POST /auth/verify-email`
**Descripción:** Verifica el email del usuario

**Body:**
```json
{
  "token": "token-de-verificacion"
}
```

---

#### `POST /auth/request-password-reset`
**Descripción:** Solicita un reseteo de contraseña (envía email)

**Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

---

#### `POST /auth/reset-password`
**Descripción:** Resetea la contraseña con el token recibido por email

**Body:**
```json
{
  "token": "token-de-reseteo",
  "new_password": "NuevaPass123"
}
```

---

#### `GET /auth/me`
**Descripción:** Obtiene el perfil del usuario autenticado

**Headers:** Requiere autenticación

**Respuesta:** `UserProfile`

---

#### `GET /auth/validate-token`
**Descripción:** Valida si un token JWT es válido

**Headers:** Requiere autenticación

---

### 👤 Usuarios (`/users`)

#### `GET /users/me`
**Descripción:** Obtiene el perfil del usuario autenticado

**Headers:** Requiere autenticación

---

#### `PUT /users/me`
**Descripción:** Actualiza el perfil del usuario autenticado

**Headers:** Requiere autenticación

**Body:**
```json
{
  "full_name": "Nuevo Nombre",
  "phone": "+57 300 123 4567",
  "timezone": "America/Bogota"
}
```

---

#### `POST /users/me/change-password`
**Descripción:** Cambia la contraseña del usuario autenticado

**Headers:** Requiere autenticación

**Body:**
```json
{
  "current_password": "PasswordActual123",
  "new_password": "NuevaPassword123"
}
```

---

#### `POST /users/me/deactivate`
**Descripción:** Desactiva la cuenta del usuario autenticado

**Headers:** Requiere autenticación

---

#### `GET /users/me/statistics`
**Descripción:** Obtiene estadísticas del usuario (número de mascotas, etc.)

**Headers:** Requiere autenticación

---

#### `GET /users/`
**Descripción:** Lista todos los usuarios (solo admin)

**Headers:** Requiere autenticación y rol admin

**Query Parameters:**
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)
- `role`: Filtrar por rol (opcional)
- `is_active`: Filtrar por estado activo (opcional)

---

#### `GET /users/{user_id}`
**Descripción:** Obtiene un usuario por ID (solo admin)

**Headers:** Requiere autenticación y rol admin

---

#### `PUT /users/{user_id}`
**Descripción:** Actualiza un usuario por ID (solo admin)

**Headers:** Requiere autenticación y rol admin

---

#### `POST /users/{user_id}/reactivate`
**Descripción:** Reactiva un usuario desactivado (solo admin)

**Headers:** Requiere autenticación y rol admin

---

#### `DELETE /users/{user_id}`
**Descripción:** Elimina un usuario (solo admin)

**Headers:** Requiere autenticación y rol admin

---

#### `GET /users/{user_id}/statistics`
**Descripción:** Obtiene estadísticas de un usuario específico (solo admin)

**Headers:** Requiere autenticación y rol admin

---

### 🐾 Mascotas (`/pets`)

#### `GET /pets/`
**Descripción:** Obtiene todas las mascotas del usuario autenticado

**Headers:** Requiere autenticación

**Query Parameters:**
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)
- `species`: Filtrar por especie (opcional)

**Respuesta:** Lista de `PetResponse`

---

#### `GET /pets/summary`
**Descripción:** Obtiene un resumen de todas las mascotas del usuario

**Headers:** Requiere autenticación

**Respuesta:** Lista de `PetSummary`

---

#### `GET /pets/{pet_id}`
**Descripción:** Obtiene una mascota específica por ID

**Headers:** Requiere autenticación

**Respuesta:** `PetResponse`

---

#### `POST /pets/`
**Descripción:** Crea una nueva mascota

**Headers:** Requiere autenticación

**Body:**
```json
{
  "name": "Chispita",
  "species": "Canino",
  "breed": "Pinscher",
  "birth_date": "2018-11-14",
  "weight_kg": 5.5,
  "sex": "Hembra",
  "notes": "Muy juguetona"
}
```

**Respuesta:** `PetResponse`

---

#### `PUT /pets/{pet_id}`
**Descripción:** Actualiza una mascota existente

**Headers:** Requiere autenticación

**Body:** `PetUpdate` (campos opcionales)

**Respuesta:** `PetResponse`

---

#### `DELETE /pets/{pet_id}`
**Descripción:** Elimina una mascota

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

#### `GET /pets/{pet_id}/stats`
**Descripción:** Obtiene estadísticas completas de una mascota

**Headers:** Requiere autenticación

**Respuesta:** `PetWithStats` (incluye vacunaciones, desparasitaciones, visitas, etc.)

---

### 💉 Vacunaciones (`/vaccinations`)

#### `GET /vaccinations/`
**Descripción:** Lista todas las vacunaciones del usuario

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `VaccinationResponse`

---

#### `GET /vaccinations/{vaccination_id}`
**Descripción:** Obtiene una vacunación específica

**Headers:** Requiere autenticación

**Respuesta:** `VaccinationResponse`

---

#### `POST /vaccinations/`
**Descripción:** Crea un nuevo registro de vacunación

**Headers:** Requiere autenticación

**Body:**
```json
{
  "pet_id": "876835fa-6c7d-4c97-bc18-4e5728e8bc13",
  "vaccine_name": "Vanguard Plus 5 L4",
  "vaccination_date": "2019-01-17",
  "next_due_date": "2019-01-18",
  "veterinarian": "Ana Selenne Zúñiga O.",
  "notes": "Primera vacunación"
}
```

**Respuesta:** `VaccinationResponse`

---

#### `PUT /vaccinations/{vaccination_id}`
**Descripción:** Actualiza un registro de vacunación

**Headers:** Requiere autenticación

**Body:** `VaccinationUpdate` (campos opcionales)

**Respuesta:** `VaccinationResponse`

---

#### `DELETE /vaccinations/{vaccination_id}`
**Descripción:** Elimina un registro de vacunación

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

### 🪱 Desparasitaciones (`/dewormings`)

#### `GET /dewormings/`
**Descripción:** Lista todas las desparasitaciones del usuario

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `DewormingResponse`

---

#### `GET /dewormings/{deworming_id}`
**Descripción:** Obtiene una desparasitación específica

**Headers:** Requiere autenticación

**Respuesta:** `DewormingResponse`

---

#### `POST /dewormings/`
**Descripción:** Crea un nuevo registro de desparasitación

**Headers:** Requiere autenticación

**Body:**
```json
{
  "pet_id": "876835fa-6c7d-4c97-bc18-4e5728e8bc13",
  "medication_name": "Canigen L",
  "administration_date": "2019-01-30",
  "next_due_date": "2019-04-30",
  "dosage": "1 tableta",
  "veterinarian": "Ana Selenne Zúñiga O."
}
```

**Respuesta:** `DewormingResponse`

---

#### `PUT /dewormings/{deworming_id}`
**Descripción:** Actualiza un registro de desparasitación

**Headers:** Requiere autenticación

**Body:** `DewormingUpdate` (campos opcionales)

**Respuesta:** `DewormingResponse`

---

#### `DELETE /dewormings/{deworming_id}`
**Descripción:** Elimina un registro de desparasitación

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

### 🏥 Visitas Veterinarias (`/vet-visits`)

#### `GET /vet-visits/`
**Descripción:** Lista todas las visitas veterinarias del usuario

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `VetVisitResponse`

---

#### `GET /vet-visits/{visit_id}`
**Descripción:** Obtiene una visita veterinaria específica

**Headers:** Requiere autenticación

**Respuesta:** `VetVisitResponse`

---

#### `POST /vet-visits/`
**Descripción:** Crea un nuevo registro de visita veterinaria

**Headers:** Requiere autenticación

**Body:**
```json
{
  "pet_id": "876835fa-6c7d-4c97-bc18-4e5728e8bc13",
  "visit_date": "2024-01-15",
  "veterinarian": "Dr. Ana Zúñiga",
  "reason": "Chequeo general",
  "diagnosis": "Saludable",
  "treatment": "Ninguno",
  "notes": "Mascota en buen estado"
}
```

**Respuesta:** `VetVisitResponse`

---

#### `PUT /vet-visits/{visit_id}`
**Descripción:** Actualiza un registro de visita veterinaria

**Headers:** Requiere autenticación

**Body:** `VetVisitUpdate` (campos opcionales)

**Respuesta:** `VetVisitResponse`

---

#### `DELETE /vet-visits/{visit_id}`
**Descripción:** Elimina un registro de visita veterinaria

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

### 🍽️ Planes de Nutrición (`/nutrition-plans`)

#### `GET /nutrition-plans/`
**Descripción:** Lista todos los planes de nutrición del usuario

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `NutritionPlanResponse`

---

#### `GET /nutrition-plans/summary`
**Descripción:** Obtiene un resumen de todos los planes de nutrición

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)

**Respuesta:** Lista de `NutritionPlanSummary`

---

#### `GET /nutrition-plans/{plan_id}`
**Descripción:** Obtiene un plan de nutrición específico

**Headers:** Requiere autenticación

**Respuesta:** `NutritionPlanResponse`

---

#### `POST /nutrition-plans/`
**Descripción:** Crea un nuevo plan de nutrición

**Headers:** Requiere autenticación

**Body:**
```json
{
  "pet_id": "876835fa-6c7d-4c97-bc18-4e5728e8bc13",
  "name": "Plan de Alimentación Diario",
  "description": "Alimentación balanceada para perro adulto",
  "calories_per_day": 800
}
```

**Respuesta:** `NutritionPlanResponse`

---

#### `PUT /nutrition-plans/{plan_id}`
**Descripción:** Actualiza un plan de nutrición

**Headers:** Requiere autenticación

**Body:** `NutritionPlanUpdate` (campos opcionales)

**Respuesta:** `NutritionPlanResponse`

---

#### `DELETE /nutrition-plans/{plan_id}`
**Descripción:** Elimina un plan de nutrición

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

#### `GET /nutrition-plans/{plan_id}/stats`
**Descripción:** Obtiene estadísticas de un plan de nutrición (incluye comidas)

**Headers:** Requiere autenticación

**Respuesta:** `NutritionPlanWithMeals`

---

#### `GET /nutrition-plans/pet/{pet_id}/active`
**Descripción:** Obtiene el plan de nutrición activo de una mascota

**Headers:** Requiere autenticación

**Respuesta:** `NutritionPlanResponse`

---

#### `POST /nutrition-plans/{plan_id}/duplicate`
**Descripción:** Duplica un plan de nutrición existente

**Headers:** Requiere autenticación

**Respuesta:** `NutritionPlanResponse` (nuevo plan creado)

---

#### `GET /nutrition-plans/pet/{pet_id}/history`
**Descripción:** Obtiene el historial de planes de nutrición de una mascota

**Headers:** Requiere autenticación

**Respuesta:** Lista de `NutritionPlanSummary`

---

### 🍖 Comidas (`/meals`)

#### `GET /meals/`
**Descripción:** Lista todas las comidas registradas del usuario

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `MealResponse`

---

#### `GET /meals/{meal_id}`
**Descripción:** Obtiene una comida específica

**Headers:** Requiere autenticación

**Respuesta:** `MealResponse`

---

#### `POST /meals/`
**Descripción:** Registra una nueva comida

**Headers:** Requiere autenticación

**Body:**
```json
{
  "nutrition_plan_id": "plan-uuid",
  "meal_date": "2024-01-15",
  "meal_time": "08:00:00",
  "food_type": "Croquetas",
  "quantity_grams": 150,
  "calories": 600,
  "notes": "Desayuno"
}
```

**Respuesta:** `MealResponse`

---

#### `PUT /meals/{meal_id}`
**Descripción:** Actualiza un registro de comida

**Headers:** Requiere autenticación

**Body:** `MealUpdate` (campos opcionales)

**Respuesta:** `MealResponse`

---

#### `DELETE /meals/{meal_id}`
**Descripción:** Elimina un registro de comida

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

### ⏰ Recordatorios (`/reminders`)

#### `GET /reminders/`
**Descripción:** Lista todos los recordatorios del usuario

**Headers:** Requiere autenticación

**Query Parameters:**
- `pet_id`: Filtrar por mascota (opcional)
- `is_active`: Filtrar por estado activo (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `ReminderResponse`

---

#### `GET /reminders/{reminder_id}`
**Descripción:** Obtiene un recordatorio específico

**Headers:** Requiere autenticación

**Respuesta:** `ReminderResponse`

---

#### `POST /reminders/`
**Descripción:** Crea un nuevo recordatorio

**Headers:** Requiere autenticación

**Body:**
```json
{
  "pet_id": "876835fa-6c7d-4c97-bc18-4e5728e8bc13",
  "title": "Vacunación anual",
  "description": "Recordar vacunación anual de Chispita",
  "reminder_date": "2024-06-15",
  "frequency": "yearly",
  "is_active": true
}
```

**Respuesta:** `ReminderResponse`

---

#### `PUT /reminders/{reminder_id}`
**Descripción:** Actualiza un recordatorio

**Headers:** Requiere autenticación

**Body:** `ReminderUpdate` (campos opcionales)

**Respuesta:** `ReminderResponse`

---

#### `DELETE /reminders/{reminder_id}`
**Descripción:** Elimina un recordatorio

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

#### `POST /reminders/process-due`
**Descripción:** Procesa recordatorios vencidos y genera notificaciones

**Headers:** Requiere autenticación

**Nota:** Este endpoint se puede llamar periódicamente para procesar recordatorios

---

### 🔔 Notificaciones (`/notifications`)

#### `GET /notifications/`
**Descripción:** Lista todas las notificaciones del usuario autenticado

**Headers:** Requiere autenticación

**Query Parameters:**
- `is_read`: Filtrar por estado de lectura (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 100)

**Respuesta:** Lista de `NotificationResponse`

---

#### `GET /notifications/{notification_id}`
**Descripción:** Obtiene una notificación específica

**Headers:** Requiere autenticación

**Respuesta:** `NotificationResponse`

---

#### `DELETE /notifications/{notification_id}`
**Descripción:** Elimina una notificación (marcar como leída)

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

### 📸 Imágenes y Documentos (`/images`)

#### `POST /images/pets/{pet_id}/profile`
**Descripción:** Sube o actualiza la foto de perfil de una mascota

**Headers:** Requiere autenticación

**Body:** `multipart/form-data`
- `file`: Archivo de imagen (jpg, jpeg, png, gif, webp)
- Tamaño máximo: 5MB
- Solo puede haber 1 foto de perfil por mascota (se reemplaza la anterior)

**Respuesta:** `ImageUploadResponse`

---

#### `POST /images/pets/{pet_id}/gallery`
**Descripción:** Sube una foto a la galería de una mascota

**Headers:** Requiere autenticación

**Body:** `multipart/form-data`
- `file`: Archivo de imagen (jpg, jpeg, png, gif, webp)
- Tamaño máximo: 5MB
- Límite: 5 fotos de galería + 1 perfil = 6 fotos totales

**Respuesta:** `ImageUploadResponse`

---

#### `POST /images/pets/{pet_id}/documents`
**Descripción:** Sube un documento PDF de una mascota

**Headers:** Requiere autenticación

**Body:** `multipart/form-data`
- `file`: Archivo PDF
- `document_category`: Categoría del documento (opcional)
  - Opciones: `vaccination`, `vet_visit`, `lab_result`, `general`
- `description`: Descripción del documento (opcional)
- Tamaño máximo: 10MB

**⚠️ IMPORTANTE:** Los documentos PDF deben contener **texto extraíble** para que el Chat IA pueda analizarlos. Los PDFs que son solo imágenes (sin OCR) no pueden ser analizados.

**Respuesta:** `DocumentUploadResponse`

---

#### `GET /images/pets/{pet_id}/documents`
**Descripción:** Lista todos los documentos PDF de una mascota

**Headers:** Requiere autenticación

**Query Parameters:**
- `category`: Filtrar por categoría (opcional)
  - Opciones: `vaccination`, `vet_visit`, `lab_result`, `general`

**Respuesta:** Lista de `PetPhotoListResponse`

---

#### `GET /images/pets/{pet_id}/photos`
**Descripción:** Lista todas las fotos (perfil + galería) de una mascota

**Headers:** Requiere autenticación

**Query Parameters:**
- `is_profile`: Filtrar solo fotos de perfil (opcional)

**Respuesta:** Lista de `PetPhotoListResponse`

---

#### `GET /images/pets/{pet_id}/photos/{photo_id}`
**Descripción:** Obtiene una foto específica

**Headers:** Requiere autenticación

**Respuesta:** `PetPhotoListResponse`

---

#### `DELETE /images/pets/{pet_id}/photos/{photo_id}`
**Descripción:** Elimina una foto o documento

**Headers:** Requiere autenticación

**Status:** 204 No Content

---

### 🤖 Chat IA Veterinario (`/chat`)

#### `POST /chat/pets/{pet_id}/ask`
**Descripción:** Hace una pregunta sobre la salud de una mascota usando IA

**Headers:** Requiere autenticación

**Body:**
```json
{
  "question": "¿Puedes leer el documento de vacunación de mi mascota?",
  "session_id": "optional-session-id"
}
```

**Parámetros:**
- `pet_id` (path): UUID de la mascota
- `question` (body, requerido): La pregunta que quieres hacer
- `session_id` (body, opcional): ID de sesión para mantener el contexto. Si no se proporciona, se genera automáticamente como `{user_id}_{pet_id}`

**Respuesta:**
```json
{
  "answer": "Claro, María. He revisado el documento de vacunación de Chispita...",
  "source_documents": [
    {
      "content": "CERTIFICADO DE VACUNACIÓN VETERINARIA\nDATOS DE LA MASCOTA:\n- Nombre: Chispita...",
      "source": "https://pet-healthcare.s3.us-east-1.amazonaws.com/pets/.../document.pdf",
      "page": 0
    }
  ],
  "chat_history": [
    {
      "role": "user",
      "content": "¿Puedes leer el documento de vacunación de chispita?"
    },
    {
      "role": "assistant",
      "content": "Claro, María. He revisado el documento..."
    }
  ],
  "has_documents": true,
  "session_id": "user123_pet456",
  "error": null
}
```

**Características:**
- Funciona como veterinario experto incluso sin documentos
- Analiza documentos PDF con texto extraíble
- Mantiene memoria conversacional por sesión
- Responde preguntas generales sobre salud animal

---

#### `GET /chat/sessions/{session_id}/history`
**Descripción:** Obtiene el historial completo de una conversación

**Headers:** Requiere autenticación

**Respuesta:**
```json
{
  "session_id": "user123_pet456",
  "history": [
    {
      "role": "user",
      "content": "Mi perra se llama Chispita y tiene fiebre"
    },
    {
      "role": "assistant",
      "content": "Lamento saber que Chispita no se siente bien..."
    }
  ]
}
```

---

#### `DELETE /chat/sessions/{session_id}`
**Descripción:** Limpia el historial de una conversación (borra la memoria)

**Headers:** Requiere autenticación

**Respuesta:**
```json
{
  "message": "Conversación limpiada correctamente",
  "session_id": "user123_pet456"
}
```

---

### 📊 Logs de Auditoría (`/audit-logs`)

#### `GET /audit-logs/`
**Descripción:** Obtiene todos los logs de auditoría con filtros

**Headers:** Requiere autenticación

**Permisos:**
- **Admin:** Puede ver todos los logs
- **Usuario:** Solo ve sus propios logs

**Query Parameters:**
- `actor_user_id`: Filtrar por usuario (opcional)
- `action`: Filtrar por acción (opcional, búsqueda parcial)
- `object_type`: Filtrar por tipo de objeto (opcional)
- `object_id`: Filtrar por ID de objeto (opcional)
- `date_from`: Logs desde esta fecha (opcional)
- `date_to`: Logs hasta esta fecha (opcional)
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 1000)

**Respuesta:** Lista de `AuditLogWithUser`

---

### 🔄 Reseteo de Contraseña (`/password-resets`)

#### `POST /password-resets/request`
**Descripción:** Solicita un reseteo de contraseña (envía email)

**Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

---

#### `POST /password-resets/confirm`
**Descripción:** Confirma y completa el reseteo de contraseña

**Body:**
```json
{
  "token": "token-de-reseteo",
  "new_password": "NuevaPassword123"
}
```

---

## 💬 Chat IA Veterinario - Guía Detallada

### 📋 Descripción General

El sistema de Chat IA Veterinario permite a los usuarios hacer preguntas sobre la salud y cuidado de sus mascotas utilizando inteligencia artificial. El sistema funciona como un veterinario experto que puede:

- Responder preguntas generales sobre salud animal
- Analizar documentos médicos de las mascotas (PDFs con texto)
- Mantener memoria conversacional para recordar preguntas anteriores
- Proporcionar recomendaciones profesionales basadas en el contexto

---

### 🔐 Requisitos Previos

Para usar el Chat IA Veterinario, necesitas:

1. **Autenticación**: Debes estar logueado en el sistema
   - Obtener un token JWT mediante el endpoint `/auth/login`
   - Incluir el token en el header `Authorization: Bearer <token>`

2. **Mascota registrada**: Debes tener al menos una mascota registrada en el sistema
   - Obtener el `pet_id` de tu mascota (UUID)

3. **Documentos (opcional pero recomendado)**: 
   - Los documentos PDF deben contener **texto extraíble**
   - ⚠️ **IMPORTANTE**: Los documentos que son solo imágenes (sin texto OCR) no pueden ser analizados
   - Para que el sistema pueda leer documentos, estos deben ser PDFs con texto seleccionable o haber sido procesados con OCR

---

### 💡 Casos de Uso

#### Caso 1: Pregunta General sobre Salud

**Pregunta:** "Mi perra se llama Chispita y tiene fiebre y está decaída, ¿qué puede ser?"

**Respuesta:** El sistema responderá como veterinario experto, proporcionando posibles causas y recomendaciones, incluso sin documentos.

#### Caso 2: Consulta sobre Documentos

**Pregunta:** "¿Puedes leer el documento de vacunación de Chispita?"

**Respuesta:** Si hay un PDF de vacunación con texto extraíble, el sistema:
- Leerá el documento
- Extraerá la información relevante
- Proporcionará un resumen estructurado
- Mencionará fechas, vacunas aplicadas, lotes, etc.

#### Caso 3: Preguntas de Seguimiento con Memoria

**Pregunta 1:** "Mi perra se llama Chispita y tiene fiebre"
**Pregunta 2:** "¿Cómo se llama mi perra?"

**Respuesta:** El sistema recordará que la perra se llama Chispita gracias a la memoria conversacional.

#### Caso 4: Análisis de Historial Médico

**Pregunta:** "¿Cuándo fue la última vacunación de Chispita?"

**Respuesta:** Si hay documentos de vacunación, el sistema buscará y proporcionará la fecha exacta y detalles de la vacunación.

---

### ⚠️ Importante sobre Documentos

#### Documentos que FUNCIONAN ✅
- PDFs con texto seleccionable (texto nativo)
- PDFs procesados con OCR (reconocimiento óptico de caracteres)
- Documentos escaneados que han sido convertidos a texto

#### Documentos que NO FUNCIONAN ❌
- Imágenes JPG/PNG sin procesar
- PDFs que son solo imágenes sin OCR
- Documentos escaneados sin procesamiento de texto

#### Recomendaciones
1. Si subes un documento escaneado, asegúrate de que haya sido procesado con OCR
2. Los documentos con texto nativo funcionan mejor y más rápido
3. El sistema puede analizar múltiples documentos PDF de la misma mascota

---

### 🔄 Gestión de Sesiones

#### ¿Qué es una Sesión?

Una sesión mantiene el contexto de la conversación. Todas las preguntas dentro de la misma sesión comparten el historial.

#### Generación Automática de Session ID

Si no proporcionas un `session_id`, el sistema genera uno automáticamente:
```
session_id = "{user_id}_{pet_id}"
```

**Ejemplo:** `0cda74e5-67c4-4262-912c-7695e01d8dcf_876835fa-6c7d-4c97-bc18-4e5728e8bc13`

#### Usar Session ID Personalizado

Puedes proporcionar tu propio `session_id` para:
- Mantener conversaciones separadas para la misma mascota
- Organizar conversaciones por tema
- Compartir sesiones entre dispositivos

**Ejemplo:**
```json
{
  "question": "¿Cuándo fue la última vacunación?",
  "session_id": "consulta-vacunacion-2024"
}
```

---

### 📝 Ejemplos de Preguntas

#### Preguntas Generales
- "¿Qué síntomas tiene un perro con moquillo?"
- "¿Cómo debo alimentar a mi gato?"
- "Mi gallina tiene moquillo, ¿qué hago?"
- "¿Cuándo debo vacunar a mi cachorro?"

#### Preguntas sobre Documentos
- "¿Puedes leer el documento de vacunación de [nombre mascota]?"
- "¿Qué información contiene el historial médico?"
- "¿Cuándo fue la última visita al veterinario?"
- "¿Qué vacunas tiene aplicadas mi mascota?"

#### Preguntas de Seguimiento (usando memoria)
- "¿Recuerdas lo que te pregunté antes?"
- "¿Cómo se llama mi mascota?"
- "Basándote en lo que vimos, ¿qué recomiendas?"

---

### 🛠️ Ejemplo Completo con cURL

```bash
# 1. Hacer una pregunta
curl -X 'POST' \
  'https://pet-healthcare-back.onrender.com/chat/pets/876835fa-6c7d-4c97-bc18-4e5728e8bc13/ask' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "¿Puedes leer el documento de vacunación de mi mascota?",
    "session_id": "consulta-2024-01-15"
  }'

# 2. Obtener historial
curl -X 'GET' \
  'https://pet-healthcare-back.onrender.com/chat/sessions/consulta-2024-01-15/history' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'

# 3. Limpiar conversación
curl -X 'DELETE' \
  'https://pet-healthcare-back.onrender.com/chat/sessions/consulta-2024-01-15' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

---

## 🐛 Solución de Problemas

### Error: "pgvector extension not found"

**Local:**
```bash
sudo -u postgres psql -d pet_health_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Render:**
- Verifica que tu plan de PostgreSQL soporte extensiones
- Contacta soporte de Render si el problema persiste

---

### Error: "OPENAI_API_KEY not found"

**Local:**
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Verifica que la variable se llama exactamente `OPENAI_API_KEY`
- Reinicia el servidor después de agregar las variables

**Render:**
- Verifica que agregaste la variable en "Environment Variables"
- Verifica que no tiene espacios extra
- Haz un redeploy después de agregar variables

---

### Error: "No module named 'langchain'"

**Local:**
```bash
pip install -r requirements.txt --force-reinstall
```

**Render:**
- Verifica que `requirements.txt` está en el repositorio
- Verifica los logs del build en Render
- Haz un redeploy limpio

---

### Error al procesar PDFs

- Verifica que los PDFs están accesibles desde S3
- Verifica que tienes permisos para leer desde S3
- Revisa los logs del servidor para más detalles
- **Importante:** Verifica que el PDF tiene texto extraíble (no es solo una imagen)

---

### Error de conexión a PostgreSQL

**Local:**
- Verifica que PostgreSQL está corriendo: `sudo systemctl status postgresql`
- Verifica que `DATABASE_URL` en `.env` es correcta
- Verifica que el usuario tiene permisos en la base de datos

**Render:**
- Verifica que `DATABASE_URL` está configurada automáticamente
- Verifica que la base de datos está activa en Render

---

### Error 401: No Autenticado

```json
{
  "detail": "Not authenticated"
}
```

**Solución:** Verifica que el token JWT sea válido y esté incluido en el header `Authorization: Bearer <token>`

---

### Error 404: Mascota No Encontrada

```json
{
  "detail": "Mascota no encontrada o no pertenece al usuario"
}
```

**Solución:** Verifica que el `pet_id` sea correcto y que la mascota pertenezca al usuario autenticado

---

### Error 500: Error del Servidor

```json
{
  "answer": "Error procesando la pregunta: ...",
  "error": "..."
}
```

**Solución:** Revisa los logs del servidor o contacta al administrador

---

## 📊 Límites y Consideraciones

### Memoria Conversacional
- La memoria se mantiene mientras la sesión esté activa
- Se limita a un número máximo de mensajes para evitar consumo excesivo
- La memoria se pierde si se limpia la sesión o se reinicia el servidor

### Documentos
- El sistema puede procesar múltiples documentos PDF por mascota
- Los documentos se indexan automáticamente cuando se suben
- El análisis puede tardar unos segundos en documentos grandes

### Rate Limiting
- Respeta los límites de la API de OpenAI
- Las respuestas pueden tardar entre 2-10 segundos dependiendo de la complejidad

---

## ✅ Checklist de Instalación

### 🖥️ Local
- [ ] pgvector instalado en PostgreSQL
- [ ] Extensión `vector` creada en la base de datos `pet_health_tracker`
- [ ] Dependencias de Python instaladas (`pip install -r requirements.txt`)
- [ ] Variables de entorno configuradas en `.env`
- [ ] `OPENAI_API_KEY` configurada
- [ ] Servidor iniciado sin errores (`uvicorn app.main:app --reload`)
- [ ] Endpoint `/chat/pets/{pet_id}/ask` funciona
- [ ] Documentos PDF se procesan correctamente

### ☁️ Render
- [ ] Extensión `vector` creada en la base de datos de Render
- [ ] Variables de entorno configuradas en el dashboard de Render
- [ ] `OPENAI_API_KEY` configurada en Render
- [ ] Deploy completado sin errores
- [ ] Endpoint `/chat/pets/{pet_id}/ask` funciona en producción
- [ ] Documentos PDF se procesan correctamente

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, podrás:
- ✅ Gestionar usuarios y mascotas
- ✅ Registrar vacunaciones, desparasitaciones y visitas veterinarias
- ✅ Crear planes de nutrición y registrar comidas
- ✅ Configurar recordatorios y recibir notificaciones
- ✅ Subir imágenes y documentos
- ✅ **Hacer preguntas sobre los documentos PDF de tus mascotas usando IA con contexto conversacional**

---

## 📞 Resumen Rápido

**Para empezar rápido:**

1. **Local:**
   ```bash
   # Instalar pgvector
   sudo apt install -y postgresql-server-dev-16 build-essential git
   cd /tmp && git clone --branch v0.4.1 https://github.com/pgvector/pgvector.git
   cd pgvector && make && sudo make install
   sudo -u postgres psql -d pet_health_tracker -c "CREATE EXTENSION vector;"
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Agregar variables al .env (ver PARTE 3)
   
   # Iniciar servidor
   uvicorn app.main:app --reload
   ```

2. **Render:**
   - Crear extensión: `CREATE EXTENSION vector;` en tu DB
   - Agregar variables de entorno en el dashboard
   - Hacer deploy

---

**¿Necesitas ayuda?** Revisa la sección "Solución de Problemas" o los logs del servidor.

---

**Última actualización:** Enero 2025  
**Versión de la API:** 2.0.0


