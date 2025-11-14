# 🧪 Guía Completa de Pruebas - Pet HealthCare API

## 🔄 Flujo Correcto de Autenticación

### **IMPORTANTE:** Tu API requiere verificación de email antes de poder hacer login.

---

## 📋 FLUJO COMPLETO PASO A PASO

### ✅ PASO 1: Registrar Usuario

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "julian_test",
    "email": "julian@test.com",
    "password": "SecurePass123",
    "full_name": "Julian Ortega Test",
    "phone": "+57 300 123 4567",
    "timezone": "America/Bogota"
  }'
```

**Respuesta esperada:**
```json
{
  "id": "uuid-generado",
  "username": "julian_test",
  "email": "julian@test.com",
  "email_verified": false,  // ⚠️ Aún no verificado
  "is_active": true,
  ...
}
```

---

### ✅ PASO 2: Obtener Token de Verificación (DESARROLLO)

Como no tienes configurado el envío de emails, usa este endpoint de desarrollo:

```bash
curl https://pet-healthcare-api.onrender.com/auth/dev/get-verification-token/julian@test.com
```

**Respuesta esperada:**
```json
{
  "email": "julian@test.com",
  "verification_token": "token-largo-aleatorio-aqui",
  "email_verified": false,
  "instructions": "Usa este token en POST /auth/verify-email..."
}
```

**⚠️ COPIA EL TOKEN QUE TE DA**

---

### ✅ PASO 3: Verificar Email

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "token": "PEGA-AQUI-EL-TOKEN-QUE-COPIASTE"
  }'
```

**Respuesta esperada:**
```json
{
  "message": "Email verificado exitosamente"
}
```

---

### ✅ PASO 4: Ahora SÍ puedes hacer Login

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "julian@test.com",
    "password": "SecurePass123"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**⚠️ GUARDA EL ACCESS_TOKEN - Lo necesitarás para todo lo demás**

---

## 🔑 ENDPOINTS QUE REQUIEREN AUTENTICACIÓN

Ahora que tienes tu `access_token`, puedes probar estos endpoints:

### 1️⃣ Ver tu Perfil

```bash
curl -X GET https://pet-healthcare-api.onrender.com/auth/me \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

---

### 2️⃣ Validar Token

```bash
curl -X GET https://pet-healthcare-api.onrender.com/auth/validate-token \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

**Respuesta esperada:**
```json
{
  "valid": true,
  "user_id": "tu-uuid",
  "email": "julian@test.com",
  "role": "user"
}
```

---

### 3️⃣ Decodificar Token (DESARROLLO)

Para ver qué contiene tu token:

```bash
curl -X POST "https://pet-healthcare-api.onrender.com/auth/dev/decode-token?token=TU_ACCESS_TOKEN_AQUI"
```

---

### 4️⃣ Listar Mascotas

```bash
curl -X GET https://pet-healthcare-api.onrender.com/pets/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

**Respuesta esperada (si no tienes mascotas):**
```json
[]
```

---

### 5️⃣ Refrescar Token (cuando expire)

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "TU_REFRESH_TOKEN_AQUI"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "nuevo-token-aqui",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 6️⃣ Cerrar Sesión

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/logout \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

**Respuesta esperada:**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

---

## 🔐 PROBAR RESETEO DE CONTRASEÑA

### PASO 1: Solicitar Reseteo

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "julian@test.com"
  }'
```

**Respuesta:**
```json
{
  "message": "Si el email existe, recibirás un link de reseteo"
}
```

### PASO 2: Obtener Token de Reseteo (DESARROLLO)

**Opción A: Conectarte a la base de datos en Render**

1. Ve a tu PostgreSQL Database en Render
2. Copia la "External Database URL"
3. Conéctate:

```bash
psql "EXTERNAL_DATABASE_URL_AQUI"
```

4. Ejecuta:

```sql
SELECT token, expires_at, used 
FROM petcare.password_resets 
WHERE user_id = (SELECT id FROM petcare.users WHERE email = 'julian@test.com')
ORDER BY created_at DESC 
LIMIT 1;
```

**Opción B: Si necesitas un endpoint de desarrollo**

Agregar este endpoint temporalmente en `app/routes/auth.py`:

```python
@router.get("/dev/get-password-reset-token/{email}")
def get_password_reset_token_dev(email: str, db: Session = Depends(get_db)):
    """⚠️ SOLO DESARROLLO - Obtiene el token de reseteo"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise UserNotFoundException()
    
    reset = db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id,
        PasswordReset.used == False
    ).order_by(PasswordReset.created_at.desc()).first()
    
    if not reset:
        return {"error": "No hay tokens de reseteo pendientes"}
    
    return {
        "email": email,
        "token": reset.token,
        "expires_at": reset.expires_at.isoformat(),
        "used": reset.used
    }
```

### PASO 3: Resetear Contraseña

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_DE_RESETEO_AQUI",
    "new_password": "NewSecurePass456"
  }'
```

**Respuesta:**
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

### PASO 4: Login con Nueva Contraseña

```bash
curl -X POST https://pet-healthcare-api.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "julian@test.com",
    "password": "NewSecurePass456"
  }'
```

---

## 📊 USANDO SWAGGER UI (MÁS FÁCIL)

### 1. Abre Swagger:
```
https://pet-healthcare-api.onrender.com/docs
```

### 2. Registrar Usuario:
- Expande **POST /auth/register**
- Click "Try it out"
- Completa los datos
- Click "Execute"
- **Copia el email que usaste**

### 3. Obtener Token de Verificación:
- Expande **GET /auth/dev/get-verification-token/{email}**
- Click "Try it out"
- Pega tu email
- Click "Execute"
- **Copia el verification_token**

### 4. Verificar Email:
- Expande **POST /auth/verify-email**
- Click "Try it out"
- Pega el token:
```json
{
  "token": "el-token-que-copiaste"
}
```
- Click "Execute"

### 5. Login:
- Expande **POST /auth/login**
- Click "Try it out"
- Ingresa email y password
- Click "Execute"
- **Copia el access_token**

### 6. Autorizar en Swagger:
- Click en el botón **"Authorize" 🔓** (arriba a la derecha)
- En el campo "Value" ingresa: `Bearer tu-access-token-aqui`
- Click "Authorize"
- Click "Close"

### 7. Probar Endpoints Protegidos:
Ahora todos los endpoints con el candado funcionarán:
- ✅ **GET /auth/me** - Ver tu perfil
- ✅ **GET /auth/validate-token** - Validar token
- ✅ **POST /auth/logout** - Cerrar sesión
- ✅ **GET /pets/** - Listar mascotas

---

## 🎯 SCRIPT COMPLETO DE PRUEBAS

Guarda este script como `test_complete.sh`:

```bash
#!/bin/bash

API_URL="https://pet-healthcare-api.onrender.com"
EMAIL="test_$(date +%s)@example.com"
PASSWORD="TestPass123"
USERNAME="test_$(date +%s)"

echo "🧪 Iniciando pruebas completas..."
echo "📧 Email: $EMAIL"
echo ""

# 1. Registro
echo "1️⃣  Registrando usuario..."
REGISTER=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"full_name\": \"Test User\",
    \"timezone\": \"America/Bogota\"
  }")

echo "✅ Usuario registrado"
echo ""

# 2. Obtener token de verificación
echo "2️⃣  Obteniendo token de verificación..."
VERIFY_TOKEN=$(curl -s "$API_URL/auth/dev/get-verification-token/$EMAIL" | grep -o '"verification_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$VERIFY_TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token de verificación"
    exit 1
fi

echo "✅ Token obtenido: ${VERIFY_TOKEN:0:20}..."
echo ""

# 3. Verificar email
echo "3️⃣  Verificando email..."
curl -s -X POST "$API_URL/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$VERIFY_TOKEN\"}" > /dev/null

echo "✅ Email verificado"
echo ""

# 4. Login
echo "4️⃣  Haciendo login..."
LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

ACCESS_TOKEN=$(echo $LOGIN | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Error en login"
    echo "$LOGIN"
    exit 1
fi

echo "✅ Login exitoso"
echo "🔑 Token: ${ACCESS_TOKEN:0:30}..."
echo ""

# 5. Ver perfil
echo "5️⃣  Obteniendo perfil..."
PROFILE=$(curl -s "$API_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "✅ Perfil obtenido:"
echo "$PROFILE" | grep -o '"email":"[^"]*"'
echo ""

# 6. Validar token
echo "6️⃣  Validando token..."
VALIDATE=$(curl -s "$API_URL/auth/validate-token" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "✅ Token válido:"
echo "$VALIDATE"
echo ""

# 7. Listar mascotas
echo "7️⃣  Listando mascotas..."
PETS=$(curl -s "$API_URL/pets/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "✅ Mascotas: $PETS"
echo ""

# 8. Logout
echo "8️⃣  Cerrando sesión..."
curl -s -X POST "$API_URL/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

echo "✅ Sesión cerrada"
echo ""

echo "🎉 ¡Todas las pruebas completadas exitosamente!"
```

**Ejecutar:**
```bash
chmod +x test_complete.sh
./test_complete.sh
```

---

## 🐍 SCRIPT EN PYTHON

```python
import requests
import time

API_URL = "https://pet-healthcare-api.onrender.com"
EMAIL = f"test_{int(time.time())}@example.com"
PASSWORD = "TestPass123"
USERNAME = f"test_{int(time.time())}"

print("🧪 Iniciando pruebas completas...")
print(f"📧 Email: {EMAIL}\n")

# 1. Registro
print("1️⃣  Registrando usuario...")
response = requests.post(f"{API_URL}/auth/register", json={
    "username": USERNAME,
    "email": EMAIL,
    "password": PASSWORD,
    "full_name": "Test User",
    "timezone": "America/Bogota"
})
assert response.status_code == 201, f"Error en registro: {response.text}"
print("✅ Usuario registrado\n")

# 2. Obtener token de verificación
print("2️⃣  Obteniendo token de verificación...")
response = requests.get(f"{API_URL}/auth/dev/get-verification-token/{EMAIL}")
data = response.json()
verify_token = data['verification_token']
print(f"✅ Token obtenido: {verify_token[:20]}...\n")

# 3. Verificar email
print("3️⃣  Verificando email...")
response = requests.post(f"{API_URL}/auth/verify-email", json={
    "token": verify_token
})
assert response.status_code == 200, f"Error en verificación: {response.text}"
print("✅ Email verificado\n")

# 4. Login
print("4️⃣  Haciendo login...")
response = requests.post(f"{API_URL}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
assert response.status_code == 200, f"Error en login: {response.text}"
tokens = response.json()
access_token = tokens['access_token']
print(f"✅ Login exitoso")
print(f"🔑 Token: {access_token[:30]}...\n")

# Headers con autenticación
headers = {"Authorization": f"Bearer {access_token}"}

# 5. Ver perfil
print("5️⃣  Obteniendo perfil...")
response = requests.get(f"{API_URL}/auth/me", headers=headers)
assert response.status_code == 200
profile = response.json()
print(f"✅ Perfil obtenido: {profile['email']}\n")

# 6. Validar token
print("6️⃣  Validando token...")
response = requests.get(f"{API_URL}/auth/validate-token", headers=headers)
assert response.status_code == 200
print(f"✅ Token válido: {response.json()}\n")

# 7. Listar mascotas
print("7️⃣  Listando mascotas...")
response = requests.get(f"{API_URL}/pets/", headers=headers)
assert response.status_code == 200
print(f"✅ Mascotas: {response.json()}\n")

# 8. Logout
print("8️⃣  Cerrando sesión...")
response = requests.post(f"{API_URL}/auth/logout", headers=headers)
assert response.status_code == 200
print("✅ Sesión cerrada\n")

print("🎉 ¡Todas las pruebas completadas exitosamente!")
```

---

## ⚠️ IMPORTANTE - DESACTIVAR VERIFICACIÓN DE EMAIL (Opcional)

Si quieres desactivar temporalmente la verificación de email para facilitar las pruebas, modifica `app/controllers/auth.py`:

```python
# En el método login_user, comenta o elimina estas líneas:

# Opcional: Verificar si el email está verificado
# if not user.email_verified:
#     raise EmailNotVerifiedException()
```

Luego redespliega en Render.

---

## 📝 RESUMEN DEL FLUJO CORRECTO

1. ✅ Registrar usuario → `POST /auth/register`
2. ✅ Obtener token de verificación → `GET /auth/dev/get-verification-token/{email}`
3. ✅ Verificar email → `POST /auth/verify-email`
4. ✅ Login → `POST /auth/login` ← **Ahora SÍ funciona**
5. ✅ Usar el token en endpoints protegidos

---

¿Necesitas ayuda con algún paso específico? 🚀