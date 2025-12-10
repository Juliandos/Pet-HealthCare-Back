"""
Schemas Pydantic actualizados para chat con IA veterinaria
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatQuestionRequest(BaseModel):
    """Schema para hacer una pregunta al veterinario"""
    question: str = Field(
        ..., 
        description="Pregunta sobre la mascota o consulta veterinaria general",
        min_length=1,
        max_length=2000
    )
    session_id: Optional[str] = Field(
        None, 
        description="ID de sesión para mantener contexto conversacional (se genera automáticamente si no se proporciona)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Mi perro tiene 5 años y últimamente ha estado comiendo menos. ¿Debería preocuparme?",
                "session_id": "user123_pet456"
            }
        }


class SourceDocument(BaseModel):
    """Schema para un documento fuente usado en la respuesta"""
    content: str = Field(..., description="Fragmento relevante del documento")
    source: str = Field(..., description="URL o identificador del documento")
    page: int = Field(..., description="Número de página en el documento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Vacunación antirrábica aplicada el 15/03/2024...",
                "source": "https://s3.amazonaws.com/.../vacunacion_2024.pdf",
                "page": 1
            }
        }


class ChatMessage(BaseModel):
    """Schema para un mensaje en el historial de conversación"""
    role: str = Field(
        ..., 
        description="Rol del mensaje: 'user' (usuario) o 'assistant' (veterinario)"
    )
    content: str = Field(..., description="Contenido del mensaje")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "¿Cuándo fue la última vacunación?"
            }
        }


class ChatResponse(BaseModel):
    """Schema para la respuesta del veterinario"""
    answer: str = Field(
        ..., 
        description="Respuesta del veterinario experto"
    )
    source_documents: List[SourceDocument] = Field(
        default_factory=list,
        description="Documentos PDF usados como referencia (si hay documentos disponibles)"
    )
    chat_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Historial completo de la conversación"
    )
    has_documents: bool = Field(
        ..., 
        description="Indica si hay documentos PDF disponibles para esta mascota"
    )
    session_id: Optional[str] = Field(
        None, 
        description="ID de sesión para continuar la conversación"
    )
    error: Optional[str] = Field(
        None, 
        description="Mensaje de error si algo falló (null si todo OK)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Basándome en los documentos médicos de tu mascota, la última vacunación fue el 15 de marzo de 2024 (vacuna antirrábica). Según el calendario recomendado, la próxima dosis debería aplicarse alrededor del 15 de marzo de 2025. Te recomiendo programar una cita con tu veterinario 2-3 semanas antes de esa fecha.",
                "source_documents": [
                    {
                        "content": "Vacunación antirrábica - Fecha: 15/03/2024",
                        "source": "certificado_vacunacion_2024.pdf",
                        "page": 1
                    }
                ],
                "chat_history": [
                    {
                        "role": "user",
                        "content": "¿Cuándo fue la última vacunación de mi perro?"
                    },
                    {
                        "role": "assistant",
                        "content": "Basándome en los documentos médicos..."
                    }
                ],
                "has_documents": True,
                "session_id": "user123_pet456",
                "error": None
            }
        }


class ConversationHistoryResponse(BaseModel):
    """Schema para el historial de conversación completo"""
    session_id: str = Field(..., description="ID de la sesión")
    history: List[ChatMessage] = Field(
        default_factory=list,
        description="Lista completa de mensajes en orden cronológico"
    )
    message_count: int = Field(
        default=0,
        description="Número total de mensajes en la conversación"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user123_pet456",
                "history": [
                    {
                        "role": "user",
                        "content": "¿Mi perro puede comer chocolate?"
                    },
                    {
                        "role": "assistant",
                        "content": "No, el chocolate es tóxico para los perros..."
                    },
                    {
                        "role": "user",
                        "content": "¿Qué síntomas tendría si comió un poco?"
                    },
                    {
                        "role": "assistant",
                        "content": "Los síntomas de intoxicación por chocolate incluyen..."
                    }
                ],
                "message_count": 4
            }
        }


class ClearConversationRequest(BaseModel):
    """Schema para limpiar una conversación"""
    session_id: str = Field(..., description="ID de sesión a limpiar")


class SessionStatsResponse(BaseModel):
    """Schema para estadísticas de sesión"""
    session_id: str = Field(..., description="ID de la sesión")
    message_count: int = Field(..., description="Número de mensajes en memoria")
    max_messages: int = Field(..., description="Límite máximo de mensajes")
    memory_usage: str = Field(..., description="Uso de memoria (formato: actual/máximo)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user123_pet456",
                "message_count": 8,
                "max_messages": 20,
                "memory_usage": "8/20"
            }
        }


class ActiveSessionsResponse(BaseModel):
    """Schema para lista de sesiones activas"""
    active_sessions: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de sesiones activas"
    )
    total_count: int = Field(..., description="Número total de sesiones activas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "active_sessions": [
                    "user123_pet456",
                    "user789_pet101",
                    "user456_pet789"
                ],
                "total_count": 3
            }
        }