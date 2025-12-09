# 🚀 Guía Completa: Instalación y Configuración de LangChain para Chat con IA

Esta guía unificada te ayudará a instalar y configurar el sistema de chat con IA usando LangChain para hacer preguntas sobre los documentos PDF de tus mascotas, tanto en **local** como en **Render (producción)**.

## 📋 Requisitos Previos

- Ubuntu/Linux (para local) o acceso a Render (para producción)
- Python 3.11+
- PostgreSQL 12+ (local o en Render)
- Cuentas creadas:
  - OpenAI (para API key): https://platform.openai.com/api-keys
  - LangSmith (opcional, para monitoreo): https://smith.langchain.com/

---

## 🔧 PARTE 1: Instalar pgvector en PostgreSQL

La extensión pgvector permite almacenar vectores (embeddings) en PostgreSQL.

### 🖥️ Para Desarrollo Local (Ubuntu)

```bash
# 1. Actualizar paquetes
sudo apt update

# 2. Instalar dependencias
# Nota: Reemplaza "16" con tu versión de PostgreSQL (verifica con: psql --version)
# Si tienes PostgreSQL 14: postgresql-server-dev-14
# Si tienes PostgreSQL 15: postgresql-server-dev-15
# Si tienes PostgreSQL 16: postgresql-server-dev-16
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

### ☁️ Para Producción en Render

**Método 1: Usando Render CLI (Recomendado)**
```bash
# Instalar Render CLI si no lo tienes
# npm install -g render-cli

# Conectarte a la base de datos
render psql dpg-d4b3bnvgi27c7394445g-a

# En la consola de PostgreSQL, ejecutar:
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Método 2: Usando psql directamente con la URL externa**
```bash
# Conectarte usando la URL externa de Render
psql postgresql://pet_health_tracker_user:Qee0581vKSojU9hTVqHc0v5QY9R3hOZX@dpg-d4b3bnvgi27c7394445g-a.oregon-postgres.render.com/pet_health_tracker

# En la consola de PostgreSQL, ejecutar:
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Método 3: Desde el Dashboard de Render**
1. Ve al dashboard de Render
2. Selecciona tu base de datos PostgreSQL (`pet_health_tracker`)
3. Ve a "Connect" → "Connect via psql"
4. Ejecuta: `CREATE EXTENSION IF NOT EXISTS vector;`

---

## 📦 PARTE 2: Instalar Dependencias de Python

### 🖥️ Para Desarrollo Local

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

### ☁️ Para Producción en Render

Render instalará automáticamente las dependencias desde `requirements.txt` durante el deploy. Solo asegúrate de que el archivo esté actualizado en tu repositorio.

---

## 🔐 PARTE 3: Configurar Variables de Entorno

### 🖥️ Para Desarrollo Local

Edita tu archivo `.env` en la raíz del proyecto y agrega:

```env
# ============================================
# CONFIGURACIÓN EXISTENTE (mantener)
# ============================================
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/pet_health_tracker
SECRET_KEY=tu-secret-key-super-segura
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=pet-healthcare-images

# ============================================
# OPENAI (OBLIGATORIO)
# ============================================
# Obtén tu API key en: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-tu-api-key-aqui

# Modelo de OpenAI (opcional, por defecto: gpt-4o-mini)
# Opciones: gpt-4o-mini (económico), gpt-4o (potente), gpt-4-turbo (muy potente)
OPENAI_MODEL=gpt-4o-mini

# Modelo de embeddings (opcional, por defecto: text-embedding-3-small)
# Opciones: text-embedding-3-small (económico), text-embedding-3-large (preciso)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Temperatura (0.0 = determinista, 1.0 = creativo)
# Para respuestas veterinarias, usa 0.0 para mayor precisión
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
```

### ☁️ Para Producción en Render

1. Ve al dashboard de Render
2. Selecciona tu servicio (Web Service)
3. Ve a "Environment" → "Environment Variables"
4. Agrega las siguientes variables (mismas que arriba, pero sin comentarios):

```
OPENAI_API_KEY=sk-proj-tu-api-key-aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TEMPERATURE=0.0
LANGSMITH_API_KEY=ls-tu-api-key-aqui
LANGSMITH_PROJECT=pet-healthcare
LANGSMITH_TRACING=false
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_TOP_K_RESULTS=4
```

**⚠️ Importante en Render:**
- `DATABASE_URL` ya debería estar configurada automáticamente
- No necesitas crear un archivo `.env` en Render
- Todas las variables se configuran en el dashboard

---

## 🗄️ PARTE 4: Verificar Instalación

### 🖥️ Local

```bash
# Verificar que pgvector está instalado
psql -U postgres -d pet_health_tracker -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Si no aparece, ejecuta:
psql -U postgres -d pet_health_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### ☁️ Render

Conéctate a tu base de datos en Render y ejecuta:
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 🧪 PARTE 5: Probar la Instalación

### 🖥️ Local

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Iniciar el servidor
uvicorn app.main:app --reload

# 3. Verificar que el servidor está corriendo
# Deberías ver: "🚀 Pet HealthCare API v2.0 iniciada correctamente"
```

### ☁️ Render

1. El servidor se inicia automáticamente después del deploy
2. Verifica los logs en el dashboard de Render
3. Visita: `https://tu-app.onrender.com/docs`

---

## 📝 PARTE 6: Uso de la API

### 1. Subir un documento PDF de mascota

```bash
curl -X POST "http://localhost:8000/images/pets/{pet_id}/documents" \
  -H "Authorization: Bearer TU_TOKEN" \
  -F "file=@/ruta/al/documento.pdf" \
  -F "document_category=vaccination" \
  -F "description=Certificado de vacunación"
```

**En Render:** Reemplaza `localhost:8000` con tu URL de Render.

### 2. Hacer una pregunta sobre los documentos

```bash
curl -X POST "http://localhost:8000/chat/pets/{pet_id}/ask" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuándo fue la última vacunación de mi mascota?",
    "session_id": "mi-sesion-123"
  }'
```

### 3. Mantener contexto conversacional

Usa el mismo `session_id` en múltiples preguntas:

```bash
# Primera pregunta
curl -X POST "http://localhost:8000/chat/pets/{pet_id}/ask" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué vacunas tiene mi mascota?",
    "session_id": "sesion-123"
  }'

# Segunda pregunta (mantiene contexto)
curl -X POST "http://localhost:8000/chat/pets/{pet_id}/ask" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuándo vence la próxima?",
    "session_id": "sesion-123"
  }'
```

### 4. Ver historial de conversación

```bash
curl -X GET "http://localhost:8000/chat/sessions/sesion-123/history" \
  -H "Authorization: Bearer TU_TOKEN"
```

### 5. Limpiar conversación

```bash
curl -X DELETE "http://localhost:8000/chat/sessions/sesion-123" \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## 🔍 Solución de Problemas

### Error: "pgvector extension not found"

**Local:**
```bash
sudo -u postgres psql -d pet_health_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Render:**
- Verifica que tu plan de PostgreSQL soporte extensiones
- Contacta soporte de Render si el problema persiste

### Error: "OPENAI_API_KEY not found"

**Local:**
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Verifica que la variable se llama exactamente `OPENAI_API_KEY`
- Reinicia el servidor después de agregar las variables

**Render:**
- Verifica que agregaste la variable en "Environment Variables"
- Verifica que no tiene espacios extra
- Haz un redeploy después de agregar variables

### Error: "No module named 'langchain'"

**Local:**
```bash
pip install -r requirements.txt --force-reinstall
```

**Render:**
- Verifica que `requirements.txt` está en el repositorio
- Verifica los logs del build en Render
- Haz un redeploy limpio

### Error al procesar PDFs

- Verifica que los PDFs están accesibles desde S3
- Verifica que tienes permisos para leer desde S3
- Revisa los logs del servidor para más detalles

### Error de conexión a PostgreSQL

**Local:**
- Verifica que PostgreSQL está corriendo: `sudo systemctl status postgresql`
- Verifica que `DATABASE_URL` en `.env` es correcta
- Verifica que el usuario tiene permisos en la base de datos

**Render:**
- Verifica que `DATABASE_URL` está configurada automáticamente
- Verifica que la base de datos está activa en Render

---

## 📚 Documentación de Endpoints

Una vez que el servidor esté corriendo:

- **Swagger UI (Local)**: http://localhost:8000/docs
- **Swagger UI (Render)**: https://tu-app.onrender.com/docs
- **ReDoc (Local)**: http://localhost:8000/redoc
- **ReDoc (Render)**: https://tu-app.onrender.com/redoc

---

## 🔒 Privacidad

**Importante**: Este sistema usa OpenAI para:
- Generar embeddings (vectores) de los documentos
- Generar respuestas usando GPT

Los documentos se envían a OpenAI para procesamiento. Si necesitas 100% privacidad, considera:
- Usar modelos locales (Ollama, LlamaIndex)
- Usar embeddings locales (Sentence Transformers)

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

Una vez completados todos los pasos, podrás hacer preguntas sobre los documentos PDF de tus mascotas usando IA con contexto conversacional, tanto en local como en producción.

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
   
   # Agregar variables al .env
   # (ver PARTE 3)
   
   # Iniciar servidor
   uvicorn app.main:app --reload
   ```

2. **Render:**
   - Crear extensión: `CREATE EXTENSION vector;` en tu DB
   - Agregar variables de entorno en el dashboard
   - Hacer deploy

---

**¿Necesitas ayuda?** Revisa la sección "Solución de Problemas" o los logs del servidor.

