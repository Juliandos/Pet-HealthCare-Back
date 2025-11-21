# 📚 Guía Completa de Rutas - Pet HealthCare API

**URL Base:** `https://pet-healthcare-back.onrender.com`  
**Documentación Swagger:** `https://pet-healthcare-back.onrender.com/docs`

---

## 🔐 1. AUTENTICACIÓN (`/auth`)

**Permisos:** Público (no requiere autenticación)

### 1.1 Registro de Usuario
```http
POST /auth/register
```
**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "SecurePass123",
  "username": "usuario123",  // Opcional
  "full_name": "Nombre Completo",  // Opcional
  "phone": "+57 300 123 4567",  // Opcional
  "timezone": "America/Bogota"  // Opcional
}
```
**Nota:** Envía email de verificación automáticamente (SendGrid/Resend)

### 1.2 Login
```http
POST /auth/login
```
**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "SecurePass123"
}
```
**Retorna:** `access_token` (30 min) y `refresh_token` (7 días)

### 1.3 Verificar Email
```http
POST /auth/verify-email
```
**Body:**
```json
{
  "token": "token-del-email"
}
```

### 1.4 Refresh Token
```http
POST /auth/refresh
```
**Body:**
```json
{
  "refresh_token": "tu-refresh-token"
}
```

### 1.5 Logout
```http
POST /auth/logout
```
**Headers:** `Authorization: Bearer {access_token}`

### 1.6 Solicitar Reseteo de Contraseña
```http
POST /auth/request-password-reset
```
**Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

### 1.7 Resetear Contraseña
```http
POST /auth/reset-password
```
**Body:**
```json
{
  "token": "token-del-email",
  "new_password": "NewSecurePass456"
}
```

### 1.8 Ver Perfil Actual
```http
GET /auth/me
```
**Headers:** `Authorization: Bearer {access_token}`

---

## 👤 2. USUARIOS (`/users`)

### 2.1 Perfil del Usuario Actual (USER)
```http
GET /users/me
PUT /users/me
GET /users/me/statistics
```
**Permisos:** Usuario autenticado (solo su propio perfil)

**Estadísticas incluyen:**
- Número de mascotas
- Número de recordatorios activos
- Número de notificaciones pendientes

### 2.2 Cambiar Contraseña (USER)
```http
POST /users/me/change-password
```
**Body:**
```json
{
  "current_password": "SecurePass123",
  "new_password": "NewSecurePass456"
}
```

### 2.3 Gestión de Usuarios (ADMIN)
```http
GET /users/                    # Listar todos los usuarios
GET /users/{user_id}           # Ver usuario específico
PUT /users/{user_id}           # Actualizar usuario
DELETE /users/{user_id}        # Eliminar usuario
POST /users/{user_id}/deactivate  # Desactivar usuario
POST /users/{user_id}/reactivate  # Reactivar usuario
GET /users/{user_id}/statistics   # Estadísticas del usuario
```
**Permisos:** Solo administradores

**Filtros disponibles en GET /users/:**
- `search`: Buscar por username, email o nombre
- `is_active`: Filtrar por estado activo
- `skip`: Paginación
- `limit`: Límite de resultados (máx 100)

---

## 🐾 3. MASCOTAS (`/pets`)

**Permisos:** Usuario autenticado (solo sus propias mascotas)

### 3.1 CRUD Básico
```http
GET /pets/                     # Listar todas mis mascotas
GET /pets/summary              # Resumen de mascotas
GET /pets/{pet_id}             # Ver mascota específica
POST /pets/                    # Crear nueva mascota
PUT /pets/{pet_id}             # Actualizar mascota
DELETE /pets/{pet_id}          # Eliminar mascota
```

**Filtros en GET /pets/:**
- `species`: Filtrar por especie (perro, gato, ave, etc.)
- `skip`: Paginación
- `limit`: Límite (máx 100)

**Body para crear/actualizar:**
```json
{
  "name": "Max",
  "species": "perro",
  "breed": "Labrador",
  "birth_date": "2020-01-15",
  "weight_kg": 25.5,
  "sex": "macho",
  "notes": "Muy juguetón"
}
```

### 3.2 Estadísticas de Mascota
```http
GET /pets/{pet_id}/stats
```
**Incluye:**
- Última vacunación
- Próxima vacunación
- Última desparasitación
- Próxima desparasitación
- Última visita veterinaria
- Próxima visita programada
- Total de comidas registradas
- Planes de nutrición activos

---

## 💉 4. VACUNACIONES (`/vaccinations`)

**Permisos:** Usuario autenticado (solo sus mascotas)

### CRUD Completo
```http
GET /vaccinations/              # Listar todas (filtro: ?pet_id={id})
GET /vaccinations/{id}         # Ver específica
POST /vaccinations/             # Crear nueva
PUT /vaccinations/{id}          # Actualizar
DELETE /vaccinations/{id}      # Eliminar
```

**Body ejemplo:**
```json
{
  "pet_id": "uuid-de-mascota",
  "vaccine_name": "Rabia",
  "manufacturer": "Laboratorio XYZ",
  "lot_number": "LOT123",
  "date_administered": "2024-01-15",
  "next_due": "2025-01-15",
  "veterinarian": "Dr. García",
  "notes": "Sin reacciones"
}
```

---

## 🪱 5. DESPARASITACIONES (`/dewormings`)

**Permisos:** Usuario autenticado (solo sus mascotas)

### CRUD Completo
```http
GET /dewormings/               # Listar todas (filtro: ?pet_id={id})
GET /dewormings/{id}           # Ver específica
POST /dewormings/              # Crear nueva
PUT /dewormings/{id}           # Actualizar
DELETE /dewormings/{id}        # Eliminar
```

**Body ejemplo:**
```json
{
  "pet_id": "uuid-de-mascota",
  "medication": "Praziquantel",
  "date_administered": "2024-01-15",
  "next_due": "2024-04-15",
  "veterinarian": "Dr. García",
  "notes": "Aplicado correctamente"
}
```

---

## 🏥 6. VISITAS VETERINARIAS (`/vet-visits`)

**Permisos:** Usuario autenticado (solo sus mascotas)

### CRUD Completo
```http
GET /vet-visits/               # Listar todas (filtro: ?pet_id={id})
GET /vet-visits/{id}           # Ver específica
POST /vet-visits/              # Crear nueva
PUT /vet-visits/{id}           # Actualizar
DELETE /vet-visits/{id}        # Eliminar
```

**Body ejemplo:**
```json
{
  "pet_id": "uuid-de-mascota",
  "visit_date": "2024-01-15T10:00:00Z",
  "reason": "Revisión anual",
  "diagnosis": "Saludable",
  "treatment": "Ninguno",
  "follow_up_date": "2025-01-15T10:00:00Z",
  "veterinarian": "Dr. García"
}
```

---

## 🍽️ 7. PLANES DE NUTRICIÓN (`/nutrition-plans`)

**Permisos:** Usuario autenticado (solo sus mascotas)

### CRUD Completo
```http
GET /nutrition-plans/          # Listar todos (filtro: ?pet_id={id})
GET /nutrition-plans/summary   # Resumen de planes
GET /nutrition-plans/{id}      # Ver específico
GET /nutrition-plans/{id}/meals # Ver comidas del plan
POST /nutrition-plans/         # Crear nuevo
PUT /nutrition-plans/{id}      # Actualizar
DELETE /nutrition-plans/{id}   # Eliminar
```

**Body ejemplo:**
```json
{
  "pet_id": "uuid-de-mascota",
  "name": "Plan Adulto",
  "description": "Alimentación para perro adulto",
  "calories_per_day": 1200
}
```

---

## 🍖 8. COMIDAS (`/meals`)

**Permisos:** Usuario autenticado (solo sus mascotas)

### CRUD Completo
```http
GET /meals/                    # Listar todas (filtro: ?pet_id={id})
GET /meals/{id}                # Ver específica
POST /meals/                   # Crear nueva
PUT /meals/{id}                # Actualizar
DELETE /meals/{id}             # Eliminar
```

**Body ejemplo:**
```json
{
  "pet_id": "uuid-de-mascota",
  "plan_id": "uuid-del-plan",  // Opcional
  "meal_time": "2024-01-15T08:00:00Z",
  "description": "Croquetas premium",
  "calories": 300
}
```

---

## ⏰ 9. RECORDATORIOS (`/reminders`)

**Permisos:** Usuario autenticado (solo sus recordatorios)

### CRUD Completo
```http
GET /reminders/                # Listar todos (filtros: ?pet_id={id}&is_active={true/false})
GET /reminders/{id}            # Ver específico
POST /reminders/               # Crear nuevo
PUT /reminders/{id}            # Actualizar
DELETE /reminders/{id}         # Eliminar
```

**Body ejemplo:**
```json
{
  "pet_id": "uuid-de-mascota",  // Opcional
  "title": "Vacuna anual",
  "description": "Recordatorio para vacuna de rabia",
  "event_time": "2024-12-15T10:00:00Z",
  "timezone": "America/Bogota",
  "frequency": "yearly",  // once, daily, weekly, monthly, yearly
  "is_active": true,
  "notify_by_email": true,
  "notify_in_app": true
}
```

---

## 📸 10. IMÁGENES - AWS S3 (`/images`)

**Permisos:** Usuario autenticado (solo sus mascotas)

### 10.1 Subir Foto de Perfil
```http
POST /images/pets/{pet_id}/profile
```
**Content-Type:** `multipart/form-data`  
**Body:** `file` (imagen)

**Restricciones:**
- Tamaño máximo: 5MB
- Formatos: jpg, jpeg, png, gif, webp
- Se optimiza automáticamente
- Se almacena en AWS S3

**Ejemplo con curl:**
```bash
curl -X POST "https://pet-healthcare-back.onrender.com/images/pets/{pet_id}/profile" \
  -H "Authorization: Bearer {token}" \
  -F "file=@/ruta/a/imagen.jpg"
```

### 10.2 Subir Foto a Galería
```http
POST /images/pets/{pet_id}/gallery
```
**Mismo formato que foto de perfil**

### 10.3 Listar Fotos
```http
GET /images/pets/{pet_id}/photos
```
**Retorna:** Lista con URLs de S3 y metadatos

### 10.4 Eliminar Foto Específica
```http
DELETE /images/pets/{pet_id}/photos?s3_key={clave-s3}
```
**Parámetro:** `s3_key` obtenido al listar las fotos

### 10.5 Eliminar Todas las Fotos
```http
DELETE /images/pets/{pet_id}/photos/all
```
**⚠️ Elimina permanentemente todas las fotos de la mascota**

---

## 🔔 11. NOTIFICACIONES (`/notifications`)

**Permisos:** Usuario autenticado (solo sus notificaciones)

### CRUD Completo
```http
GET /notifications/            # Listar todas
GET /notifications/{id}        # Ver específica
POST /notifications/           # Crear nueva
PUT /notifications/{id}        # Actualizar
DELETE /notifications/{id}     # Eliminar
```

**Body ejemplo:**
```json
{
  "reminder_id": "uuid-del-recordatorio",  // Opcional
  "pet_id": "uuid-de-mascota",  // Opcional
  "sent_at": "2024-01-15T10:00:00Z",
  "method": "email",
  "status": "sent",
  "provider_response": {}
}
```

---

## 📋 12. LOGS DE AUDITORÍA (`/audit-logs`)

**Permisos:**
- **USER:** Solo sus propios logs
- **ADMIN:** Todos los logs

### 12.1 Listar Logs
```http
GET /audit-logs/
```
**Filtros disponibles:**
- `actor_user_id`: Filtrar por usuario
- `action`: Filtrar por acción (búsqueda parcial)
- `object_type`: Tipo de objeto afectado
- `object_id`: ID específico del objeto
- `date_from`: Desde fecha
- `date_to`: Hasta fecha
- `skip`: Paginación
- `limit`: Límite (máx 1000)

**Ejemplo:**
```
GET /audit-logs/?action=USER_LOGIN&date_from=2024-01-01
```

### 12.2 Ver Log Específico
```http
GET /audit-logs/{id}
```

### 12.3 Crear Log (Sistema)
```http
POST /audit-logs/
```
**Nota:** Generalmente usado por el sistema internamente

---

## 🔑 13. RESETEOS DE CONTRASEÑA (`/password-resets`)

**Permisos:** 
- Público: Solicitar reseteo
- Usuario autenticado: Ver sus propios reseteos
- Admin: Ver todos los reseteos

### 13.1 Solicitar Reseteo (Público)
```http
POST /password-resets/request
```
**Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

### 13.2 Confirmar Reseteo (Público)
```http
POST /password-resets/confirm
```
**Body:**
```json
{
  "token": "token-del-email",
  "new_password": "NewSecurePass456"
}
```

### 13.3 Validar Token (Público)
```http
GET /password-resets/validate/{token}
```

### 13.4 Listar Reseteos (USER/ADMIN)
```http
GET /password-resets/
```
**Filtros:**
- `user_id`: Filtrar por usuario
- `is_used`: Filtrar por tokens usados/no usados
- `skip`: Paginación
- `limit`: Límite

---

## 🧪 GUÍA DE PRUEBAS RÁPIDAS PARA PRESENTACIÓN

### Paso 1: Autenticación
```bash
# 1. Registrar usuario
POST /auth/register
Body: {"email": "test@ejemplo.com", "password": "Test1234"}

# 2. Verificar email (copiar token del email o logs)
POST /auth/verify-email
Body: {"token": "token-del-email"}

# 3. Login
POST /auth/login
Body: {"email": "test@ejemplo.com", "password": "Test1234"}

# Guardar el access_token para los siguientes pasos
```

### Paso 2: Crear Mascota
```bash
POST /pets/
Headers: Authorization: Bearer {access_token}
Body: {
  "name": "Max",
  "species": "perro",
  "breed": "Labrador",
  "birth_date": "2020-01-15"
}

# Guardar el pet_id
```

### Paso 3: Subir Foto (S3)
```bash
POST /images/pets/{pet_id}/profile
Headers: Authorization: Bearer {access_token}
Body: multipart/form-data con archivo imagen
```

### Paso 4: Crear Registros Relacionados
```bash
# Vacunación
POST /vaccinations/
Body: {"pet_id": "{pet_id}", "vaccine_name": "Rabia", "date_administered": "2024-01-15"}

# Desparasitación
POST /dewormings/
Body: {"pet_id": "{pet_id}", "medication": "Praziquantel", "date_administered": "2024-01-15"}

# Visita Veterinaria
POST /vet-visits/
Body: {"pet_id": "{pet_id}", "visit_date": "2024-01-15T10:00:00Z", "reason": "Revisión"}

# Plan de Nutrición
POST /nutrition-plans/
Body: {"pet_id": "{pet_id}", "name": "Plan Adulto", "calories_per_day": 1200}

# Comida
POST /meals/
Body: {"pet_id": "{pet_id}", "meal_time": "2024-01-15T08:00:00Z", "calories": 300}

# Recordatorio
POST /reminders/
Body: {"pet_id": "{pet_id}", "title": "Vacuna", "event_time": "2024-12-15T10:00:00Z", "frequency": "yearly"}
```

### Paso 5: Ver Estadísticas
```bash
# Estadísticas de mascota
GET /pets/{pet_id}/stats

# Estadísticas del usuario
GET /users/me/statistics
```

### Paso 6: Funciones Admin (si eres admin)
```bash
# Listar todos los usuarios
GET /users/

# Ver logs de auditoría
GET /audit-logs/
```

---

## 📊 RESUMEN DE PERMISOS

| Endpoint | Público | User | Admin |
|----------|---------|------|-------|
| `/auth/*` | ✅ | ✅ | ✅ |
| `/users/me` | ❌ | ✅ | ✅ |
| `/users/` | ❌ | ❌ | ✅ |
| `/pets/*` | ❌ | ✅ | ✅ |
| `/vaccinations/*` | ❌ | ✅ | ✅ |
| `/dewormings/*` | ❌ | ✅ | ✅ |
| `/vet-visits/*` | ❌ | ✅ | ✅ |
| `/nutrition-plans/*` | ❌ | ✅ | ✅ |
| `/meals/*` | ❌ | ✅ | ✅ |
| `/reminders/*` | ❌ | ✅ | ✅ |
| `/images/*` | ❌ | ✅ | ✅ |
| `/notifications/*` | ❌ | ✅ | ✅ |
| `/audit-logs/` | ❌ | ✅* | ✅ |
| `/password-resets/request` | ✅ | ✅ | ✅ |
| `/password-resets/` | ❌ | ✅* | ✅ |

*Solo sus propios registros

---

## 🔗 CONEXIONES ENTRE RUTAS

### Flujo Principal:
1. **Usuario** → Crea **Mascota**
2. **Mascota** → Tiene **Vacunaciones**, **Desparasitaciones**, **Visitas Veterinarias**
3. **Mascota** → Tiene **Planes de Nutrición** → Tiene **Comidas**
4. **Mascota** → Tiene **Fotos** (almacenadas en S3)
5. **Usuario** → Crea **Recordatorios** (opcionalmente vinculados a mascota)
6. **Recordatorios** → Generan **Notificaciones**

### Relaciones:
- `pets` → `vaccinations`, `dewormings`, `vet_visits`, `nutrition_plans`, `meals`, `pet_photos`
- `users` → `pets`, `reminders`, `notifications`, `audit_logs`
- `reminders` → `notifications` (cuando se activan)
- `nutrition_plans` → `meals` (opcional)

---

## 🎯 CHECKLIST PARA PRESENTACIÓN

- [ ] ✅ Autenticación completa (registro → verificación → login)
- [ ] ✅ CRUD de Mascotas
- [ ] ✅ Subir foto a S3
- [ ] ✅ Crear vacunación
- [ ] ✅ Crear desparasitación
- [ ] ✅ Crear visita veterinaria
- [ ] ✅ Crear plan de nutrición y comida
- [ ] ✅ Crear recordatorio
- [ ] ✅ Ver estadísticas de mascota
- [ ] ✅ Ver estadísticas de usuario
- [ ] ✅ Listar fotos de mascota
- [ ] ✅ Funciones admin (si aplica)

---

## 📝 NOTAS IMPORTANTES

1. **Todos los endpoints requieren `Authorization: Bearer {token}` excepto:**
   - `/auth/register`
   - `/auth/login`
   - `/auth/verify-email`
   - `/auth/request-password-reset`
   - `/auth/reset-password`

2. **Los usuarios solo pueden acceder a sus propios datos** (excepto admins)

3. **Las imágenes se almacenan en AWS S3** y se optimizan automáticamente

4. **Los emails se envían automáticamente** al registrar y resetear contraseña (SendGrid)

5. **Los recordatorios pueden generar notificaciones** automáticamente según su configuración

---

¿Necesitas ayuda con alguna ruta específica? 🚀
