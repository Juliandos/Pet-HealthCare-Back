# Guía de Uso: Chat IA Veterinario

## 📋 Descripción General

El sistema de Chat IA Veterinario permite a los usuarios hacer preguntas sobre la salud y cuidado de sus mascotas utilizando inteligencia artificial. El sistema funciona como un veterinario experto que puede:

- Responder preguntas generales sobre salud animal
- Analizar documentos médicos de las mascotas (PDFs con texto)
- Mantener memoria conversacional para recordar preguntas anteriores
- Proporcionar recomendaciones profesionales basadas en el contexto

---

## 🔐 Requisitos Previos

Para usar el Chat IA Veterinario, necesitas:

1. **Autenticación**: Debes estar logueado en el sistema
   - Obtener un token JWT mediante el endpoint de login
   - Incluir el token en el header `Authorization: Bearer <token>`

2. **Mascota registrada**: Debes tener al menos una mascota registrada en el sistema
   - Obtener el `pet_id` de tu mascota (UUID)

3. **Documentos (opcional pero recomendado)**: 
   - Los documentos PDF deben contener **texto extraíble**
   - ⚠️ **IMPORTANTE**: Los documentos que son solo imágenes (sin texto OCR) no pueden ser analizados
   - Para que el sistema pueda leer documentos, estos deben ser PDFs con texto seleccionable o haber sido procesados con OCR

---

## 🔗 Endpoints Disponibles

### 1. Hacer una Pregunta sobre una Mascota

**Endpoint:** `POST /chat/pets/{pet_id}/ask`

**Descripción:** Permite hacer preguntas sobre la salud de una mascota. El sistema puede responder usando:
- Conocimiento general de veterinaria (siempre disponible)
- Documentos PDF de la mascota (si están disponibles y tienen texto)

**URL Base:** `https://pet-healthcare-back.onrender.com`

**URL Completa:** `https://pet-healthcare-back.onrender.com/chat/pets/{pet_id}/ask`

**Ejemplo:**
```
POST https://pet-healthcare-back.onrender.com/chat/pets/876835fa-6c7d-4c97-bc18-4e5728e8bc13/ask
```

**Headers:**
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "Content-Type": "application/json"
}
```

**Body (JSON):**
```json
{
  "question": "¿Puedes leer el documento de vacunación de mi mascota?",
  "session_id": "optional-session-id"
}
```

**Parámetros:**
- `pet_id` (path): UUID de la mascota
- `question` (body, requerido): La pregunta que quieres hacer
- `session_id` (body, opcional): ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se genera automáticamente como `{user_id}_{pet_id}`

**Respuesta Exitosa (200 OK):**
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

**Campos de la Respuesta:**
- `answer`: La respuesta del veterinario IA
- `source_documents`: Lista de fragmentos de documentos PDF que se usaron para responder (si aplica)
- `chat_history`: Historial completo de la conversación en esta sesión
- `has_documents`: Indica si hay documentos PDF disponibles para la mascota
- `session_id`: ID de la sesión de conversación
- `error`: Mensaje de error si hubo algún problema (null si todo está bien)

---

### 2. Obtener Historial de Conversación

**Endpoint:** `GET /chat/sessions/{session_id}/history`

**Descripción:** Obtiene el historial completo de una conversación específica.

**URL Completa:** `https://pet-healthcare-back.onrender.com/chat/sessions/{session_id}/history`

**Ejemplo:**
```
GET https://pet-healthcare-back.onrender.com/chat/sessions/user123_pet456/history
```

**Headers:**
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta Exitosa (200 OK):**
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
    },
    {
      "role": "user",
      "content": "¿Puedes leer el documento de vacunación?"
    },
    {
      "role": "assistant",
      "content": "Claro, María. He revisado el documento..."
    }
  ]
}
```

---

### 3. Limpiar Conversación

**Endpoint:** `DELETE /chat/sessions/{session_id}`

**Descripción:** Elimina el historial de una conversación específica, borrando la memoria del chat.

**URL Completa:** `https://pet-healthcare-back.onrender.com/chat/sessions/{session_id}`

**Ejemplo:**
```
DELETE https://pet-healthcare-back.onrender.com/chat/sessions/user123_pet456
```

**Headers:**
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Conversación limpiada correctamente",
  "session_id": "user123_pet456"
}
```

---

## 💡 Casos de Uso

### Caso 1: Pregunta General sobre Salud

**Pregunta:** "Mi perra se llama Chispita y tiene fiebre y está decaída, ¿qué puede ser?"

**Respuesta:** El sistema responderá como veterinario experto, proporcionando posibles causas y recomendaciones, incluso sin documentos.

### Caso 2: Consulta sobre Documentos

**Pregunta:** "¿Puedes leer el documento de vacunación de Chispita?"

**Respuesta:** Si hay un PDF de vacunación con texto extraíble, el sistema:
- Leerá el documento
- Extraerá la información relevante
- Proporcionará un resumen estructurado
- Mencionará fechas, vacunas aplicadas, lotes, etc.

### Caso 3: Preguntas de Seguimiento con Memoria

**Pregunta 1:** "Mi perra se llama Chispita y tiene fiebre"
**Pregunta 2:** "¿Cómo se llama mi perra?"

**Respuesta:** El sistema recordará que la perra se llama Chispita gracias a la memoria conversacional.

### Caso 4: Análisis de Historial Médico

**Pregunta:** "¿Cuándo fue la última vacunación de Chispita?"

**Respuesta:** Si hay documentos de vacunación, el sistema buscará y proporcionará la fecha exacta y detalles de la vacunación.

---

## ⚠️ Importante sobre Documentos

### Documentos que FUNCIONAN ✅
- PDFs con texto seleccionable (texto nativo)
- PDFs procesados con OCR (reconocimiento óptico de caracteres)
- Documentos escaneados que han sido convertidos a texto

### Documentos que NO FUNCIONAN ❌
- Imágenes JPG/PNG sin procesar
- PDFs que son solo imágenes sin OCR
- Documentos escaneados sin procesamiento de texto

### Recomendaciones
1. Si subes un documento escaneado, asegúrate de que haya sido procesado con OCR
2. Los documentos con texto nativo funcionan mejor y más rápido
3. El sistema puede analizar múltiples documentos PDF de la misma mascota

---

## 🔄 Gestión de Sesiones

### ¿Qué es una Sesión?

Una sesión mantiene el contexto de la conversación. Todas las preguntas dentro de la misma sesión comparten el historial.

### Generación Automática de Session ID

Si no proporcionas un `session_id`, el sistema genera uno automáticamente:
```
session_id = "{user_id}_{pet_id}"
```

**Ejemplo:** `0cda74e5-67c4-4262-912c-7695e01d8dcf_876835fa-6c7d-4c97-bc18-4e5728e8bc13`

### Usar Session ID Personalizado

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

## 📝 Ejemplos de Preguntas

### Preguntas Generales
- "¿Qué síntomas tiene un perro con moquillo?"
- "¿Cómo debo alimentar a mi gato?"
- "Mi gallina tiene moquillo, ¿qué hago?"
- "¿Cuándo debo vacunar a mi cachorro?"

### Preguntas sobre Documentos
- "¿Puedes leer el documento de vacunación de [nombre mascota]?"
- "¿Qué información contiene el historial médico?"
- "¿Cuándo fue la última visita al veterinario?"
- "¿Qué vacunas tiene aplicadas mi mascota?"

### Preguntas de Seguimiento (usando memoria)
- "¿Recuerdas lo que te pregunté antes?"
- "¿Cómo se llama mi mascota?"
- "Basándote en lo que vimos, ¿qué recomiendas?"

---

## 🛠️ Ejemplo Completo con cURL

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

## 🐛 Manejo de Errores

### Error 401: No Autenticado
```json
{
  "detail": "Not authenticated"
}
```
**Solución:** Verifica que el token JWT sea válido y esté incluido en el header.

### Error 404: Mascota No Encontrada
```json
{
  "detail": "Mascota no encontrada o no pertenece al usuario"
}
```
**Solución:** Verifica que el `pet_id` sea correcto y que la mascota pertenezca al usuario autenticado.

### Error 500: Error del Servidor
```json
{
  "answer": "Error procesando la pregunta: ...",
  "error": "..."
}
```
**Solución:** Revisa los logs del servidor o contacta al administrador.

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

## 🔗 Enlaces Relacionados

- **Documentación de la API:** `/docs` (Swagger UI)
- **Subir Documentos:** `POST /images/pets/{pet_id}/documents`
- **Listar Documentos:** `GET /images/pets/{pet_id}/documents`

---

## 📞 Soporte

Si tienes problemas o preguntas sobre el Chat IA Veterinario:
1. Revisa esta guía
2. Verifica los logs de error en la respuesta
3. Contacta al equipo de desarrollo

---

**Última actualización:** Enero 2025
**Versión de la API:** 1.0

