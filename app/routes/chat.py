"""
Rutas para el chat con IA sobre documentos de mascotas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.middleware.auth import get_current_active_user
from app.models import User
from app.controllers.chat import ChatController
from app.schemas.chat import (
    ChatQuestionRequest,
    ChatResponse,
    ClearConversationRequest,
    ConversationHistoryResponse
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat IA"]
)

def get_db():
    """Dependencia para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/pets/{pet_id}/ask",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Hacer pregunta sobre documentos de mascota",
    description="""
    Hace una pregunta sobre los documentos PDF de una mascota usando IA con LangChain.
    
    **Características:**
    - Usa RAG (Retrieval Augmented Generation) para responder basándose en los documentos
    - Mantiene contexto conversacional si se proporciona un session_id
    - Procesa múltiples PDFs de la mascota
    - Retorna documentos fuente utilizados para la respuesta
    
    **Ejemplo de preguntas:**
    - "¿Cuándo fue la última vacunación?"
    - "¿Qué medicamentos se recetaron en la última visita?"
    - "Resume el historial médico de mi mascota"
    - "¿Hay alguna alergia documentada?"
    """
)
async def ask_question_about_pet(
    pet_id: str,
    request: ChatQuestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para hacer preguntas sobre los documentos de una mascota
    """
    try:
        result = ChatController.ask_question_about_pet(
            db=db,
            pet_id=pet_id,
            question=request.question,
            current_user=current_user,
            session_id=request.session_id
        )
        
        return ChatResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando pregunta: {str(e)}"
        )

@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Limpiar conversación",
    description="Limpia la memoria de una conversación específica"
)
async def clear_conversation(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Limpia la memoria de una conversación
    """
    success = ChatController.clear_conversation(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    return {"message": "Conversación limpiada correctamente", "session_id": session_id}

@router.get(
    "/sessions/{session_id}/history",
    response_model=ConversationHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener historial de conversación",
    description="Obtiene el historial de mensajes de una sesión de conversación"
)
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el historial de una conversación
    """
    history = ChatController.get_conversation_history(session_id)
    
    return ConversationHistoryResponse(
        session_id=session_id,
        history=history
    )

