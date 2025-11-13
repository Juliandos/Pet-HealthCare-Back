from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append({
            "field": field,
            "message": message,
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Error de validación en los datos enviados",
            "errors": errors
        }
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Maneja errores de integridad de base de datos (duplicados, violaciones de FK, etc.)"""
    error_message = str(exc.orig)
    
    # Detectar tipo de error
    if "duplicate key" in error_message or "UNIQUE constraint" in error_message:
        message = "Ya existe un registro con esos datos"
        if "email" in error_message:
            message = "Ya existe un usuario con ese email"
        elif "username" in error_message:
            message = "Ya existe un usuario con ese nombre de usuario"
    elif "foreign key" in error_message:
        message = "El registro relacionado no existe"
    else:
        message = "Error de integridad en la base de datos"
    
    logger.error(f"Integrity error on {request.url}: {error_message}")
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "status": "error",
            "message": message,
            "detail": "Verifica que los datos sean correctos y no estén duplicados"
        }
    )

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Maneja errores generales de SQLAlchemy"""
    logger.error(f"Database error on {request.url}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Error al procesar la operación en la base de datos",
            "detail": "Por favor intenta nuevamente. Si el error persiste, contacta al soporte"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones generales no capturadas"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Ha ocurrido un error inesperado",
            "detail": "Nuestro equipo ha sido notificado y está trabajando en solucionarlo"
        }
    )

def setup_error_handlers(app):
    """Configura todos los manejadores de errores en la aplicación"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)