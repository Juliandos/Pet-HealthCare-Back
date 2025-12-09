"""
Schemas para el chat con IA sobre documentos de mascotas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatQuestionRequest(BaseModel):
    """Schema para hacer una pregunta"""
    question: str = Field(..., description="Pregunta sobre los documentos de la mascota", min_length=1)
    session_id: Optional[str] = Field(None, description="ID de sesión para mantener contexto conversacional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "¿Cuándo fue la última vacunación de mi mascota?",
                "session_id": "optional-session-id"
            }
        }

class SourceDocument(BaseModel):
    """Schema para un documento fuente"""
    content: str = Field(..., description="Fragmento del documento")
    source: str = Field(..., description="URL o fuente del documento")
    page: int = Field(..., description="Número de página")

class ChatMessage(BaseModel):
    """Schema para un mensaje en el historial"""
    role: str = Field(..., description="Rol: 'user' o 'assistant'")
    content: str = Field(..., description="Contenido del mensaje")

class ChatResponse(BaseModel):
    """Schema para la respuesta del chat"""
    answer: str = Field(..., description="Respuesta de la IA")
    source_documents: List[SourceDocument] = Field(default_factory=list, description="Documentos fuente utilizados")
    chat_history: List[ChatMessage] = Field(default_factory=list, description="Historial de conversación")
    has_documents: bool = Field(..., description="Indica si hay documentos disponibles")
    session_id: Optional[str] = Field(None, description="ID de sesión")
    error: Optional[str] = Field(None, description="Mensaje de error si hubo algún problema")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Según los documentos, la última vacunación fue el 15 de marzo de 2024.",
                "source_documents": [
                    {
                        "content": "Vacunación realizada el 15/03/2024...",
                        "source": "https://s3.../vaccination.pdf",
                        "page": 1
                    }
                ],
                "chat_history": [
                    {"role": "user", "content": "¿Cuándo fue la última vacunación?"},
                    {"role": "assistant", "content": "Según los documentos..."}
                ],
                "has_documents": True,
                "session_id": "user-id_pet-id"
            }
        }

class ClearConversationRequest(BaseModel):
    """Schema para limpiar una conversación"""
    session_id: str = Field(..., description="ID de sesión a limpiar")

class ConversationHistoryResponse(BaseModel):
    """Schema para el historial de conversación"""
    session_id: str = Field(..., description="ID de sesión")
    history: List[ChatMessage] = Field(default_factory=list, description="Historial de mensajes")

