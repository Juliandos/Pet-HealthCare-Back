"""
Schemas Pydantic para chat con IA veterinaria
Incluye configuración de memoria conversacional
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
                "question": "Mi perro se llama Max y tiene 5 años. Últimamente come menos, ¿debería preocuparme?",
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
        description="Historial completo de la conversación (últimas 6 interacciones)"
    )
    has_documents: bool = Field(
        ..., 
        description="Indica si hay documentos PDF disponibles para esta mascota"
    )
    session_id: Optional[str] = Field(
        None, 
        description="ID de sesión para continuar la conversación"
    )
    memory_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Información sobre el estado de la memoria"
    )
    error: Optional[str] = Field(
        None, 
        description="Mensaje de error si algo falló (null si todo OK)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Basándome en lo que me contaste sobre Max, tu perro de 5 años que come menos últimamente, te recomiendo observar otros síntomas como letargo, vómitos o cambios en el comportamiento. La disminución del apetito puede tener varias causas...",
                "source_documents": [],
                "chat_history": [
                    {
                        "role": "user",
                        "content": "Mi perro se llama Max y tiene 5 años. Últimamente come menos, ¿debería preocuparme?"
                    },
                    {
                        "role": "assistant",
                        "content": "Basándome en lo que me contaste sobre Max..."
                    }
                ],
                "has_documents": False,
                "session_id": "user123_pet456",
                "memory_info": {
                    "current_messages": 2,
                    "max_messages": 12,
                    "interactions_count": 1,
                    "max_interactions": 6
                },
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
    interactions_count: int = Field(
        default=0,
        description="Número de interacciones (pares pregunta-respuesta)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user123_pet456",
                "history": [
                    {
                        "role": "user",
                        "content": "Mi perro se llama Max"
                    },
                    {
                        "role": "assistant",
                        "content": "Encantado de conocer a Max. ¿En qué puedo ayudarte con él?"
                    },
                    {
                        "role": "user",
                        "content": "¿Cómo se llama mi perro?"
                    },
                    {
                        "role": "assistant",
                        "content": "Tu perro se llama Max, como me contaste anteriormente."
                    }
                ],
                "message_count": 4,
                "interactions_count": 2
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
    interactions_count: int = Field(..., description="Número de interacciones")
    max_interactions: int = Field(..., description="Límite máximo de interacciones")
    memory_usage: str = Field(..., description="Uso de memoria (formato: actual/máximo)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user123_pet456",
                "message_count": 8,
                "max_messages": 12,
                "interactions_count": 4,
                "max_interactions": 6,
                "memory_usage": "4/6 interacciones (8/12 mensajes)"
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