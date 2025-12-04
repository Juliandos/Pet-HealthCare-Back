"""
Script para probar todas las rutas de la API Pet HealthCare
Excluye las rutas de autenticación (/auth)
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

BASE_URL = "https://pet-healthcare-back.onrender.com"
EMAIL = "julian@example.com"
PASSWORD = "Password123"

# Almacenar datos creados para limpieza
created_resources: Dict[str, List[str]] = {
    "pets": [],
    "vaccinations": [],
    "dewormings": [],
    "vet_visits": [],
    "nutrition_plans": [],
    "meals": [],
    "reminders": [],
    "photos": []  # Para almacenar photo_ids
}

# Ruta de la imagen para pruebas (Windows y WSL)
IMAGE_PATH_WINDOWS = r"C:\Users\ASUS\Downloads\bull1jpg.jpg"
IMAGE_PATH_WSL = "/mnt/c/Users/ASUS/Downloads/bull1jpg.jpg"

# Reporte de resultados
report: List[Dict[str, Any]] = []

def log_test(endpoint: str, method: str, status_code: int, response_data: Any, error: Optional[str] = None):
    """Registra el resultado de una prueba"""
    report.append({
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "success": 200 <= status_code < 300,
        "response": response_data if isinstance(response_data, (dict, list, str)) else str(response_data)[:500],
        "error": error,
        "timestamp": datetime.now().isoformat()
    })
    
    status_emoji = "✅" if 200 <= status_code < 300 else "❌"
    print(f"{status_emoji} {method} {endpoint} - Status: {status_code}")

def make_request(method: str, endpoint: str, token: Optional[str] = None, 
                data: Optional[Dict] = None, files: Optional[Dict] = None) -> requests.Response:
    """Realiza una petición HTTP"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if files:
        # Para multipart/form-data
        response = requests.request(method, url, headers=headers, files=files, data=data)
    elif data and method in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = "application/json"
        response = requests.request(method, url, headers=headers, json=data)
    else:
        response = requests.request(method, url, headers=headers)
    
    return response

def login() -> Optional[str]:
    """Realiza login y retorna el access token"""
    print("\n🔐 Iniciando sesión...")
    response = make_request("POST", "/auth/login", data={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        log_test("/auth/login", "POST", response.status_code, data)
        print(f"✅ Login exitoso. Token obtenido.")
        return token
    else:
        log_test("/auth/login", "POST", response.status_code, response.text, "Error en login")
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return None

# ============================================
# PRUEBAS DE RUTAS
# ============================================

def test_users_routes(token: str):
    """Prueba las rutas de usuarios"""
    print("\n👤 Probando rutas de usuarios...")
    
    # GET /users/me
    response = make_request("GET", "/users/me", token)
    log_test("/users/me", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # PUT /users/me
    response = make_request("PUT", "/users/me", token, data={
        "full_name": "Julian Test User",
        "phone": "+57 300 123 4567"
    })
    log_test("/users/me", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # GET /users/me/statistics
    response = make_request("GET", "/users/me/statistics", token)
    log_test("/users/me/statistics", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # POST /users/me/change-password (solo probamos, no cambiamos realmente)
    # response = make_request("POST", "/users/me/change-password", token, data={
    #     "current_password": PASSWORD,
    #     "new_password": "newpass123"
    # })
    # log_test("/users/me/change-password", "POST", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_pets_routes(token: str):
    """Prueba las rutas de mascotas"""
    print("\n🐾 Probando rutas de mascotas...")
    
    # GET /pets/
    response = make_request("GET", "/pets/", token)
    existing_pets = []
    if response.status_code == 200:
        existing_pets = response.json()
    log_test("/pets/", "GET", response.status_code, existing_pets if response.status_code == 200 else response.text)
    
    # GET /pets/summary
    response = make_request("GET", "/pets/summary", token)
    log_test("/pets/summary", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # POST /pets/ - Crear una mascota de prueba
    pet_data = {
        "name": "Test Pet",
        "species": "perro",
        "breed": "Labrador",
        "birth_date": "2020-01-15",
        "weight_kg": 25.5,
        "sex": "macho",
        "notes": "Mascota de prueba para testing"
    }
    response = make_request("POST", "/pets/", token, data=pet_data)
    test_pet_id = None
    if response.status_code == 201:
        test_pet = response.json()
        test_pet_id = test_pet.get("id")
        created_resources["pets"].append(test_pet_id)
        log_test("/pets/", "POST", response.status_code, test_pet)
    else:
        log_test("/pets/", "POST", response.status_code, response.text, "Error creando mascota")
        # Si no podemos crear, usar la primera existente
        if existing_pets and len(existing_pets) > 0:
            test_pet_id = existing_pets[0].get("id")
    
    if test_pet_id:
        # GET /pets/{pet_id}
        response = make_request("GET", f"/pets/{test_pet_id}", token)
        log_test(f"/pets/{test_pet_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # GET /pets/{pet_id}/stats
        response = make_request("GET", f"/pets/{test_pet_id}/stats", token)
        log_test(f"/pets/{test_pet_id}/stats", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /pets/{pet_id}
        response = make_request("PUT", f"/pets/{test_pet_id}", token, data={
            "name": "Test Pet Updated",
            "weight_kg": 26.0
        })
        log_test(f"/pets/{test_pet_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        return test_pet_id
    
    return None

def test_vaccinations_routes(token: str, pet_id: Optional[str]):
    """Prueba las rutas de vacunaciones"""
    print("\n💉 Probando rutas de vacunaciones...")
    
    if not pet_id:
        print("⚠️ No hay pet_id disponible, saltando vacunaciones")
        return
    
    # GET /vaccinations/
    response = make_request("GET", "/vaccinations/", token)
    existing_vaccinations = []
    if response.status_code == 200:
        existing_vaccinations = response.json()
    log_test("/vaccinations/", "GET", response.status_code, existing_vaccinations if response.status_code == 200 else response.text)
    
    # POST /vaccinations/ - Crear vacunación de prueba
    vaccination_data = {
        "pet_id": pet_id,
        "vaccine_name": "Rabia",
        "date_administered": (datetime.now() - timedelta(days=30)).date().isoformat(),  # ✅ Formato date
        "next_due": (datetime.now() + timedelta(days=335)).date().isoformat(),  # ✅ Formato date
        "manufacturer": "Pfizer",
        "lot_number": "TEST-001",
        "veterinarian": "Dr. Test",
        "notes": "Vacunación de prueba"
    }
    response = make_request("POST", "/vaccinations/", token, data=vaccination_data)
    test_vaccination_id = None
    if response.status_code == 201:
        test_vaccination = response.json()
        test_vaccination_id = test_vaccination.get("id")
        created_resources["vaccinations"].append(test_vaccination_id)
        log_test("/vaccinations/", "POST", response.status_code, test_vaccination)
    else:
        log_test("/vaccinations/", "POST", response.status_code, response.text, "Error creando vacunación")
        if existing_vaccinations and len(existing_vaccinations) > 0:
            test_vaccination_id = existing_vaccinations[0].get("id")
    
    if test_vaccination_id:
        # GET /vaccinations/{vaccination_id}
        response = make_request("GET", f"/vaccinations/{test_vaccination_id}", token)
        log_test(f"/vaccinations/{test_vaccination_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /vaccinations/{vaccination_id}
        response = make_request("PUT", f"/vaccinations/{test_vaccination_id}", token, data={
            "vaccine_name": "Rabia Actualizada",
            "notes": "Notas actualizadas"
        })
        log_test(f"/vaccinations/{test_vaccination_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # DELETE /vaccinations/{vaccination_id}
        response = make_request("DELETE", f"/vaccinations/{test_vaccination_id}", token)
        log_test(f"/vaccinations/{test_vaccination_id}", "DELETE", response.status_code, "Deleted" if response.status_code == 204 else response.text)

def test_dewormings_routes(token: str, pet_id: Optional[str]):
    """Prueba las rutas de desparasitaciones"""
    print("\n🐛 Probando rutas de desparasitaciones...")
    
    if not pet_id:
        print("⚠️ No hay pet_id disponible, saltando desparasitaciones")
        return
    
    # GET /dewormings/
    response = make_request("GET", "/dewormings/", token)
    existing_dewormings = []
    if response.status_code == 200:
        existing_dewormings = response.json()
    log_test("/dewormings/", "GET", response.status_code, existing_dewormings if response.status_code == 200 else response.text)
    
    # POST /dewormings/ - Crear desparasitación de prueba
    deworming_data = {
        "pet_id": pet_id,
        "medication": "Praziquantel",
        "date_administered": (datetime.now() - timedelta(days=15)).date().isoformat(),  # ✅ Formato date
        "next_due": (datetime.now() + timedelta(days=75)).date().isoformat(),  # ✅ Formato date
        "veterinarian": "Dr. Test",
        "notes": "Desparasitación de prueba"
    }
    response = make_request("POST", "/dewormings/", token, data=deworming_data)
    test_deworming_id = None
    if response.status_code == 201:
        test_deworming = response.json()
        test_deworming_id = test_deworming.get("id")
        created_resources["dewormings"].append(test_deworming_id)
        log_test("/dewormings/", "POST", response.status_code, test_deworming)
    else:
        log_test("/dewormings/", "POST", response.status_code, response.text, "Error creando desparasitación")
        if existing_dewormings and len(existing_dewormings) > 0:
            test_deworming_id = existing_dewormings[0].get("id")
    
    if test_deworming_id:
        # GET /dewormings/{deworming_id}
        response = make_request("GET", f"/dewormings/{test_deworming_id}", token)
        log_test(f"/dewormings/{test_deworming_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /dewormings/{deworming_id}
        response = make_request("PUT", f"/dewormings/{test_deworming_id}", token, data={
            "medication": "Praziquantel Actualizado",
            "notes": "Notas actualizadas"
        })
        log_test(f"/dewormings/{test_deworming_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # DELETE /dewormings/{deworming_id}
        response = make_request("DELETE", f"/dewormings/{test_deworming_id}", token)
        log_test(f"/dewormings/{test_deworming_id}", "DELETE", response.status_code, "Deleted" if response.status_code == 204 else response.text)

def test_vet_visits_routes(token: str, pet_id: Optional[str]):
    """Prueba las rutas de visitas veterinarias"""
    print("\n🏥 Probando rutas de visitas veterinarias...")
    
    if not pet_id:
        print("⚠️ No hay pet_id disponible, saltando visitas veterinarias")
        return
    
    # GET /vet-visits/
    response = make_request("GET", "/vet-visits/", token)
    existing_visits = []
    if response.status_code == 200:
        existing_visits = response.json()
    log_test("/vet-visits/", "GET", response.status_code, existing_visits if response.status_code == 200 else response.text)
    
    # POST /vet-visits/ - Crear visita de prueba
    visit_data = {
        "pet_id": pet_id,
        "visit_date": datetime.now().isoformat(),
        "reason": "Revisión general",
        "diagnosis": "Saludable",
        "treatment": "Ninguno",
        "veterinarian": "Dr. Test",
        "notes": "Visita de prueba"
    }
    response = make_request("POST", "/vet-visits/", token, data=visit_data)
    test_visit_id = None
    if response.status_code == 201:
        test_visit = response.json()
        test_visit_id = test_visit.get("id")
        created_resources["vet_visits"].append(test_visit_id)
        log_test("/vet-visits/", "POST", response.status_code, test_visit)
    else:
        log_test("/vet-visits/", "POST", response.status_code, response.text, "Error creando visita")
        if existing_visits and len(existing_visits) > 0:
            test_visit_id = existing_visits[0].get("id")
    
    if test_visit_id:
        # GET /vet-visits/{visit_id}
        response = make_request("GET", f"/vet-visits/{test_visit_id}", token)
        log_test(f"/vet-visits/{test_visit_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /vet-visits/{visit_id}
        response = make_request("PUT", f"/vet-visits/{test_visit_id}", token, data={
            "reason": "Revisión actualizada",
            "notes": "Notas actualizadas"
        })
        log_test(f"/vet-visits/{test_visit_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # DELETE /vet-visits/{visit_id}
        response = make_request("DELETE", f"/vet-visits/{test_visit_id}", token)
        log_test(f"/vet-visits/{test_visit_id}", "DELETE", response.status_code, "Deleted" if response.status_code == 204 else response.text)

def test_nutrition_plans_routes(token: str, pet_id: Optional[str]):
    """Prueba las rutas de planes de nutrición"""
    print("\n🍽️ Probando rutas de planes de nutrición...")
    
    if not pet_id:
        print("⚠️ No hay pet_id disponible, saltando planes de nutrición")
        return
    
    # GET /nutrition-plans/
    response = make_request("GET", "/nutrition-plans/", token)
    existing_plans = []
    if response.status_code == 200:
        existing_plans = response.json()
    log_test("/nutrition-plans/", "GET", response.status_code, existing_plans if response.status_code == 200 else response.text)
    
    # GET /nutrition-plans/summary
    response = make_request("GET", "/nutrition-plans/summary", token)
    log_test("/nutrition-plans/summary", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # POST /nutrition-plans/ - Crear plan de prueba
    plan_data = {
        "pet_id": pet_id,
        "name": "Plan de Prueba",
        "description": "Plan de nutrición para testing",
        "calories_per_day": 1200
    }
    response = make_request("POST", "/nutrition-plans/", token, data=plan_data)
    test_plan_id = None
    if response.status_code == 201:
        test_plan = response.json()
        test_plan_id = test_plan.get("id")
        created_resources["nutrition_plans"].append(test_plan_id)
        log_test("/nutrition-plans/", "POST", response.status_code, test_plan)
    else:
        log_test("/nutrition-plans/", "POST", response.status_code, response.text, "Error creando plan")
        if existing_plans and len(existing_plans) > 0:
            test_plan_id = existing_plans[0].get("id")
    
    if test_plan_id:
        # GET /nutrition-plans/{plan_id}
        response = make_request("GET", f"/nutrition-plans/{test_plan_id}", token)
        log_test(f"/nutrition-plans/{test_plan_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /nutrition-plans/{plan_id}
        response = make_request("PUT", f"/nutrition-plans/{test_plan_id}", token, data={
            "name": "Plan Actualizado",
            "calories_per_day": 1300
        })
        log_test(f"/nutrition-plans/{test_plan_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        return test_plan_id
    
    return None

def test_meals_routes(token: str, pet_id: Optional[str], plan_id: Optional[str]):
    """Prueba las rutas de comidas"""
    print("\n🍖 Probando rutas de comidas...")
    
    if not pet_id:
        print("⚠️ No hay pet_id disponible, saltando comidas")
        return
    
    # GET /meals/
    response = make_request("GET", "/meals/", token)
    existing_meals = []
    if response.status_code == 200:
        existing_meals = response.json()
    log_test("/meals/", "GET", response.status_code, existing_meals if response.status_code == 200 else response.text)
    
    # POST /meals/ - Crear comida de prueba
    meal_data = {
        "pet_id": pet_id,
        "meal_time": datetime.now().isoformat(),
        "description": "Croquetas premium",
        "calories": 300
    }
    if plan_id:
        meal_data["plan_id"] = plan_id
    
    response = make_request("POST", "/meals/", token, data=meal_data)
    test_meal_id = None
    if response.status_code == 201:
        test_meal = response.json()
        test_meal_id = test_meal.get("id")
        created_resources["meals"].append(test_meal_id)
        log_test("/meals/", "POST", response.status_code, test_meal)
    else:
        log_test("/meals/", "POST", response.status_code, response.text, "Error creando comida")
        if existing_meals and len(existing_meals) > 0:
            test_meal_id = existing_meals[0].get("id")
    
    if test_meal_id:
        # GET /meals/{meal_id}
        response = make_request("GET", f"/meals/{test_meal_id}", token)
        log_test(f"/meals/{test_meal_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /meals/{meal_id}
        response = make_request("PUT", f"/meals/{test_meal_id}", token, data={
            "description": "Croquetas actualizadas",
            "calories": 350
        })
        log_test(f"/meals/{test_meal_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # DELETE /meals/{meal_id}
        response = make_request("DELETE", f"/meals/{test_meal_id}", token)
        log_test(f"/meals/{test_meal_id}", "DELETE", response.status_code, "Deleted" if response.status_code == 204 else response.text)

def test_reminders_routes(token: str, pet_id: Optional[str]):
    """Prueba las rutas de recordatorios"""
    print("\n⏰ Probando rutas de recordatorios...")
    
    # GET /reminders/
    response = make_request("GET", "/reminders/", token)
    existing_reminders = []
    if response.status_code == 200:
        existing_reminders = response.json()
    log_test("/reminders/", "GET", response.status_code, existing_reminders if response.status_code == 200 else response.text)
    
    # POST /reminders/ - Crear recordatorio de prueba
    reminder_data = {
        "title": "Recordatorio de Prueba",
        "description": "Recordatorio para testing",
        "event_time": (datetime.now() + timedelta(days=30)).isoformat(),
        "timezone": "America/Bogota",
        "frequency": "once",
        "is_active": True,
        "notify_by_email": False,
        "notify_in_app": True
    }
    if pet_id:
        reminder_data["pet_id"] = pet_id
    
    response = make_request("POST", "/reminders/", token, data=reminder_data)
    test_reminder_id = None
    if response.status_code == 201:
        test_reminder = response.json()
        test_reminder_id = test_reminder.get("id")
        created_resources["reminders"].append(test_reminder_id)
        log_test("/reminders/", "POST", response.status_code, test_reminder)
    else:
        log_test("/reminders/", "POST", response.status_code, response.text, "Error creando recordatorio")
        if existing_reminders and len(existing_reminders) > 0:
            test_reminder_id = existing_reminders[0].get("id")
    
    if test_reminder_id:
        # GET /reminders/{reminder_id}
        response = make_request("GET", f"/reminders/{test_reminder_id}", token)
        log_test(f"/reminders/{test_reminder_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # PUT /reminders/{reminder_id}
        response = make_request("PUT", f"/reminders/{test_reminder_id}", token, data={
            "title": "Recordatorio Actualizado",
            "description": "Descripción actualizada"
        })
        log_test(f"/reminders/{test_reminder_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)
        
        # DELETE /reminders/{reminder_id}
        response = make_request("DELETE", f"/reminders/{test_reminder_id}", token)
        log_test(f"/reminders/{test_reminder_id}", "DELETE", response.status_code, "Deleted" if response.status_code == 204 else response.text)

def test_notifications_routes(token: str):
    """Prueba las rutas de notificaciones"""
    print("\n📬 Probando rutas de notificaciones...")
    
    # GET /notifications/
    response = make_request("GET", "/notifications/", token)
    log_test("/notifications/", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
    
    # Si hay notificaciones, probar GET y PUT de una específica
    if response.status_code == 200:
        notifications = response.json()
        if isinstance(notifications, list) and len(notifications) > 0:
            notification_id = notifications[0].get("id")
            if notification_id:
                # GET /notifications/{notification_id}
                response = make_request("GET", f"/notifications/{notification_id}", token)
                log_test(f"/notifications/{notification_id}", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)
                
                # PUT /notifications/{notification_id} - Marcar como leída
                response = make_request("PUT", f"/notifications/{notification_id}", token, data={
                    "is_read": True
                })
                log_test(f"/notifications/{notification_id}", "PUT", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_images_routes(token: str, pet_id: Optional[str]):
    """Prueba las rutas de imágenes"""
    print("\n📸 Probando rutas de imágenes...")
    
    if not pet_id:
        print("⚠️ No hay pet_id disponible, saltando imágenes")
        return
    
    # GET /images/pets/{pet_id}/photos - Listar todas las fotos
    response = make_request("GET", f"/images/pets/{pet_id}/photos", token)
    existing_photos = []
    if response.status_code == 200:
        existing_photos = response.json()
    log_test(f"/images/pets/{pet_id}/photos", "GET", response.status_code, existing_photos if response.status_code == 200 else response.text)
    
    # POST /images/pets/{pet_id}/profile - Subir foto de perfil
    import os
    # Intentar encontrar la imagen en Windows o WSL
    image_path = None
    if os.path.exists(IMAGE_PATH_WINDOWS):
        image_path = IMAGE_PATH_WINDOWS
    elif os.path.exists(IMAGE_PATH_WSL):
        image_path = IMAGE_PATH_WSL
    
    if image_path:
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                url = f"{BASE_URL}/images/pets/{pet_id}/profile"
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(url, headers=headers, files=files)
                if response.status_code == 201:
                    photo_data = response.json()
                    photo_id = photo_data.get("photo_id")
                    if photo_id:
                        created_resources["photos"].append((pet_id, photo_id))
                    log_test(f"/images/pets/{pet_id}/profile", "POST", response.status_code, photo_data)
                else:
                    log_test(f"/images/pets/{pet_id}/profile", "POST", response.status_code, response.text, "Error subiendo foto de perfil")
        except Exception as e:
            log_test(f"/images/pets/{pet_id}/profile", "POST", 500, str(e), f"Error leyendo archivo: {str(e)}")
    else:
        print(f"⚠️ Imagen no encontrada en {IMAGE_PATH_WINDOWS} ni {IMAGE_PATH_WSL}, saltando subida de fotos")
        log_test(f"/images/pets/{pet_id}/profile", "POST", 0, None, f"Archivo no encontrado")
    
    # GET /images/pets/{pet_id}/photos - Verificar que se subió
    response = make_request("GET", f"/images/pets/{pet_id}/photos", token)
    if response.status_code == 200:
        photos = response.json()
        if photos and len(photos) > 0:
            # DELETE /images/pets/{pet_id}/photos/{photo_id} - Eliminar foto de prueba
            test_photo_id = photos[0].get("id")
            if test_photo_id:
                response = make_request("DELETE", f"/images/pets/{pet_id}/photos/{test_photo_id}", token)
                log_test(f"/images/pets/{pet_id}/photos/{test_photo_id}", "DELETE", response.status_code, "Deleted" if response.status_code == 204 else response.text)

def test_audit_logs_routes(token: str):
    """Prueba las rutas de logs de auditoría"""
    print("\n📋 Probando rutas de logs de auditoría...")
    
    # GET /audit-logs/
    response = make_request("GET", "/audit-logs/", token)
    log_test("/audit-logs/", "GET", response.status_code, response.json() if response.status_code == 200 else response.text)

def test_password_resets_routes():
    """Prueba las rutas de reseteo de contraseña (solo request, no requiere auth)"""
    print("\n🔑 Probando rutas de reseteo de contraseña...")
    
    # POST /password-resets/request (público)
    response = make_request("POST", "/password-resets/request", data={
        "email": EMAIL
    })
    log_test("/password-resets/request", "POST", response.status_code, response.json() if response.status_code == 200 else response.text)

# ============================================
# LIMPIEZA DE RECURSOS CREADOS
# ============================================

def cleanup_resources(token: str):
    """Elimina todos los recursos creados durante las pruebas"""
    print("\n🧹 Limpiando recursos creados...")
    
    # Eliminar en orden inverso (dependencias primero)
    # Nota: Los recursos ya fueron eliminados durante las pruebas individuales
    # Solo limpiamos los que quedaron sin eliminar
    
    for pet_id, photo_id in created_resources["photos"]:
        response = make_request("DELETE", f"/images/pets/{pet_id}/photos/{photo_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /images/pets/{pet_id}/photos/{photo_id}")
    
    for reminder_id in created_resources["reminders"]:
        response = make_request("DELETE", f"/reminders/{reminder_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /reminders/{reminder_id}")
    
    for meal_id in created_resources["meals"]:
        response = make_request("DELETE", f"/meals/{meal_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /meals/{meal_id}")
    
    for plan_id in created_resources["nutrition_plans"]:
        response = make_request("DELETE", f"/nutrition-plans/{plan_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /nutrition-plans/{plan_id}")
    
    for visit_id in created_resources["vet_visits"]:
        response = make_request("DELETE", f"/vet-visits/{visit_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /vet-visits/{visit_id}")
    
    for deworming_id in created_resources["dewormings"]:
        response = make_request("DELETE", f"/dewormings/{deworming_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /dewormings/{deworming_id}")
    
    for vaccination_id in created_resources["vaccinations"]:
        response = make_request("DELETE", f"/vaccinations/{vaccination_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /vaccinations/{vaccination_id}")
    
    for pet_id in created_resources["pets"]:
        response = make_request("DELETE", f"/pets/{pet_id}", token)
        print(f"  {'✅' if response.status_code == 204 else '❌'} DELETE /pets/{pet_id}")

# ============================================
# GENERAR REPORTE
# ============================================

def generate_report():
    """Genera un reporte completo de las pruebas"""
    print("\n" + "="*80)
    print("📊 REPORTE DE PRUEBAS - Pet HealthCare API")
    print("="*80)
    
    total_tests = len(report)
    successful_tests = sum(1 for r in report if r["success"])
    failed_tests = total_tests - successful_tests
    
    print(f"\n📈 RESUMEN:")
    print(f"  Total de pruebas: {total_tests}")
    print(f"  ✅ Exitosas: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"  ❌ Fallidas: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    print(f"\n📋 DETALLE DE PRUEBAS:")
    print("-" * 80)
    
    for i, test in enumerate(report, 1):
        status_emoji = "✅" if test["success"] else "❌"
        print(f"\n{i}. {status_emoji} {test['method']} {test['endpoint']}")
        print(f"   Status: {test['status_code']}")
        if test["error"]:
            print(f"   Error: {test['error']}")
        if not test["success"]:
            print(f"   Respuesta: {str(test['response'])[:200]}")
    
    # Agrupar por endpoint
    print(f"\n📊 POR ENDPOINT:")
    print("-" * 80)
    endpoint_stats = {}
    for test in report:
        endpoint = test["endpoint"]
        if endpoint not in endpoint_stats:
            endpoint_stats[endpoint] = {"total": 0, "success": 0, "failed": 0}
        endpoint_stats[endpoint]["total"] += 1
        if test["success"]:
            endpoint_stats[endpoint]["success"] += 1
        else:
            endpoint_stats[endpoint]["failed"] += 1
    
    for endpoint, stats in sorted(endpoint_stats.items()):
        success_rate = stats["success"] / stats["total"] * 100
        print(f"  {endpoint}: {stats['success']}/{stats['total']} exitosas ({success_rate:.1f}%)")
    
    # Guardar reporte en archivo JSON
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests/total_tests*100 if total_tests > 0 else 0
            },
            "tests": report,
            "endpoint_stats": endpoint_stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: {report_file}")
    print("="*80)

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("="*80)
    print("🧪 INICIANDO PRUEBAS DE RUTAS - Pet HealthCare API")
    print("="*80)
    print(f"URL Base: {BASE_URL}")
    print(f"Usuario: {EMAIL}")
    print("="*80)
    
    # 1. Login
    token = login()
    if not token:
        print("❌ No se pudo obtener el token. Abortando pruebas.")
        return
    
    # 2. Probar todas las rutas
    test_users_routes(token)
    pet_id = test_pets_routes(token)
    test_vaccinations_routes(token, pet_id)
    test_dewormings_routes(token, pet_id)
    test_vet_visits_routes(token, pet_id)
    plan_id = test_nutrition_plans_routes(token, pet_id)
    test_meals_routes(token, pet_id, plan_id)
    test_reminders_routes(token, pet_id)
    test_notifications_routes(token)
    test_images_routes(token, pet_id)
    test_audit_logs_routes(token)
    test_password_resets_routes()
    
    # 3. Limpiar recursos creados
    cleanup_resources(token)
    
    # 4. Generar reporte
    generate_report()
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main()

