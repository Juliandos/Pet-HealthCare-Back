from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine
from app.middleware.error_handler import setup_error_handlers

# Importar TODAS las rutas
from app.routes import (
    auth,
    pets,
    vaccinations,
    dewormings,
    vet_visits,
    nutrition_plans,
    meals,
    reminders,
    notifications,
    pet_photos,
    users,
    audit_logs,
    password_resets
)

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación
app = FastAPI(
    title="Pet HealthCare API",
    description="API REST completa para gestión de salud de mascotas con autenticación JWT",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (permite peticiones desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar manejadores de errores globales
setup_error_handlers(app)

# ============================================
# INCLUIR TODAS LAS RUTAS
# ============================================
app.include_router(auth.router)              # Autenticación
app.include_router(pets.router)              # Mascotas
app.include_router(vaccinations.router)      # Vacunaciones
app.include_router(dewormings.router)        # Desparasitaciones
app.include_router(vet_visits.router)        # Visitas veterinarias
app.include_router(nutrition_plans.router)   # Planes de nutrición
app.include_router(meals.router)             # Comidas
app.include_router(reminders.router)         # Recordatorios
app.include_router(notifications.router)     # Notificaciones
app.include_router(pet_photos.router)        # Fotos de mascotas
app.include_router(users.router)             # Usuarios
app.include_router(audit_logs.router)       # Registros de auditoría
app.include_router(password_resets.router)   # Reseteos de contraseña

@app.get("/")
def root():
    """Endpoint raíz que confirma que la API está funcionando"""
    return {
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
            "pet_photos": "/pet-photos"
        }
    }

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de salud de la API"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
    }

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    print("="*60)
    print("🚀 Pet HealthCare API v2.0 iniciada correctamente")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("🔐 Endpoints protegidos con JWT")
    print("="*60)

# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Pet HealthCare API detenida")