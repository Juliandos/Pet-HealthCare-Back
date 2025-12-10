"""
Rutas mejoradas para chat con IA veterinaria
Incluye endpoints para gestión de sesiones y estadísticas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.middleware.auth import get_current_active_user
from app.models import User
from app.controllers.chat import ChatController
from app.schemas.chat import (
    ChatQuestionRequest,
    ChatResponse,
    ConversationHistoryResponse
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat IA Veterinaria"]
)

def get_db():
    """Dependencia para sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/pets/{pet_id}/ask",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar veterinario experto con IA",
    description="""
    Realiza consultas a un veterinario experto con IA que mantiene memoria conversacional.
    
    **Características:**
    - 🧠 **Memoria Conversacional**: Recuerda toda la conversación previa
    - 📚 **RAG Opcional**: Usa documentos PDF de la mascota como contexto adicional
    - 🩺 **Veterinario Experto**: Especializado en todas las especies domésticas
    - 💬 **Seguimiento**: Puedes hacer preguntas como "¿recuerdas lo que mencionaste?"
    
    **Ejemplos de preguntas:**
    - "Mi perro tiene fiebre y está decaído, ¿qué puede ser?"
    - "¿Cuándo fue la última vacunación?" (si hay documentos)
    - "¿Recuerdas los síntomas que mencioné? ¿Qué tratamiento recomiendas?"
    - "¿Qué alimentos son tóxicos para gatos?"
    - "Mi ave tiene las plumas erizadas, ¿es grave?"
    
    **Session ID:**
    - Si no proporcionas `session_id`, se crea automáticamente como `{user_id}_{pet_id}`
    - Usa el mismo `session_id` para mantener contexto en múltiples preguntas
    """
)
async def ask_veterinary_question(
    pet_id: str,
    request: ChatQuestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Consulta al veterinario experto con IA sobre tu mascota
    
    **Respuesta incluye:**
    - `answer`: Respuesta del veterinario experto
    - `chat_history`: Historial completo de la conversación
    - `source_documents`: Documentos PDF usados como referencia (si aplica)
    - `has_documents`: Indica si hay documentos disponibles
    - `session_id`: ID de sesión para continuar la conversación
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
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error en endpoint de chat: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando pregunta: {str(e)}"
        )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Limpiar conversación",
    description="""
    Elimina el historial de una conversación específica.
    
    Útil cuando:
    - Quieres empezar una nueva conversación desde cero
    - El contexto de la conversación ya no es relevante
    - Quieres liberar memoria del servidor
    
    **Nota:** Esto NO afecta los documentos de la mascota, solo la memoria de la conversación.
    """
)
async def clear_conversation(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Limpia la memoria conversacional de una sesión específica
    """
    success = ChatController.clear_conversation(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesión '{session_id}' no encontrada o ya fue eliminada"
        )
    
    return {
        "message": "Conversación limpiada correctamente",
        "session_id": session_id,
        "status": "success"
    }


@router.get(
    "/sessions/{session_id}/history",
    response_model=ConversationHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener historial de conversación",
    description="""
    Obtiene el historial completo de mensajes de una sesión.
    
    **Incluye:**
    - Todos los mensajes del usuario (role: "user")
    - Todas las respuestas del veterinario (role: "assistant")
    - Orden cronológico desde el inicio de la conversación
    
    **Útil para:**
    - Revisar toda la conversación
    - Exportar el historial
    - Análisis de la consulta
    """
)
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el historial completo de una conversación
    """
    history = ChatController.get_conversation_history(session_id)
    
    return ConversationHistoryResponse(
        session_id=session_id,
        history=history,
        message_count=len(history)
    )


@router.get(
    "/sessions",
    status_code=status.HTTP_200_OK,
    summary="Listar sesiones activas",
    description="Obtiene lista de todas las sesiones de chat activas en el servidor"
)
async def list_active_sessions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas las sesiones de chat activas
    
    **Nota:** Solo para monitoreo, muestra todas las sesiones del servidor
    """
    sessions = ChatController.get_active_sessions()
    
    return {
        "active_sessions": sessions,
        "total_count": len(sessions)
    }


@router.get(
    "/sessions/{session_id}/stats",
    status_code=status.HTTP_200_OK,
    summary="Estadísticas de sesión",
    description="Obtiene estadísticas de uso de memoria y mensajes de una sesión"
)
async def get_session_statistics(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de una sesión específica
    
    **Incluye:**
    - Número de mensajes en memoria
    - Límite máximo de mensajes
    - Porcentaje de uso de memoria
    """
    stats = ChatController.get_session_stats(session_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesión '{session_id}' no encontrada"
        )
    
    return stats


@router.post(
    "/test",
    status_code=status.HTTP_200_OK,
    summary="Probar chat sin mascota",
    description="""
    Endpoint de prueba para consultas veterinarias generales sin asociar a una mascota.
    
    **Útil para:**
    - Preguntas generales sobre veterinaria
    - Probar el sistema de chat
    - Consultas sin documentos
    
    **Nota:** No mantiene memoria conversacional entre llamadas
    """
)
async def test_veterinary_chat(
    question: str = Query(..., description="Pregunta para el veterinario"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Prueba rápida del sistema de chat sin asociar a una mascota
    """
    from app.services.langchain_service import LangChainService
    from langchain.memory import ConversationBufferMemory
    
    try:
        langchain_service = LangChainService()
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="answer"
        )
        
        result = langchain_service.ask_question(
            question=question,
            vector_store=None,
            memory=memory,
            use_documents=False
        )
        
        return {
            "answer": result.get("answer"),
            "chat_history": result.get("chat_history", []),
            "mode": "test_mode",
            "note": "Esta respuesta no se guarda en ninguna sesión"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )