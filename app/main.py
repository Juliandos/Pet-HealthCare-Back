from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine
from app.routes import pets, auth
from app.middleware.error_handler import setup_error_handlers

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación
app = FastAPI(
    title="Pet HealthCare API",
    description="API REST para gestión de salud de mascotas con autenticación JWT",
    version="1.0.0",
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

# Incluir rutas
app.include_router(auth.router)  # Rutas de autenticación
app.include_router(pets.router)  # Rutas de mascotas

@app.get("/")
def root():
    """Endpoint raíz que confirma que la API está funcionando"""
    return {
        "message": "🐾 Pet HealthCare API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de salud de la API"""
    return {
        "status": "healthy",
        "database": "connected"
    }

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    print("🚀 Pet HealthCare API iniciada correctamente")
    print("📚 Documentación disponible en: http://localhost:8000/docs")

# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Pet HealthCare API detenida")