"""
Controlador para el chat con IA sobre documentos de mascotas
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models import User, Pet
from app.services.langchain_service import LangChainService
from app.controllers.pets import PetController
from langchain.memory import ConversationBufferMemory
import uuid

class ChatController:
    """Controlador para operaciones de chat con IA"""
    
    # Almacenar memorias de conversación por sesión (en producción usar Redis o DB)
    _conversation_memories: Dict[str, ConversationBufferMemory] = {}
    
    @staticmethod
    def get_pet_by_id(db: Session, pet_id: str, current_user: User) -> Pet:
        """
        Verifica que la mascota existe y pertenece al usuario
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            current_user: Usuario actual
            
        Returns:
            Instancia de Pet
        """
        return PetController.get_pet_by_id(db, pet_id, current_user)
    
    @staticmethod
    def ask_question_about_pet(
        db: Session,
        pet_id: str,
        question: str,
        current_user: User,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hace una pregunta sobre los documentos de una mascota usando IA
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            question: Pregunta del usuario
            current_user: Usuario actual
            session_id: ID de sesión para mantener contexto (opcional)
            
        Returns:
            Dict con la respuesta y metadata
        """
        # Verificar que la mascota pertenece al usuario
        pet = ChatController.get_pet_by_id(db, pet_id, current_user)
        
        # Inicializar servicio LangChain
        langchain_service = LangChainService()
        
        # Obtener URLs de documentos de la mascota
        pdf_urls = langchain_service.get_pet_documents_from_db(db, pet_id)
        
        if not pdf_urls:
            return {
                "answer": "No hay documentos disponibles para esta mascota. Por favor, sube algunos documentos PDF primero.",
                "source_documents": [],
                "chat_history": [],
                "has_documents": False
            }
        
        # Crear o obtener vector store
        try:
            vector_store = langchain_service.create_vector_store(
                pdf_urls=pdf_urls,
                pet_id=pet_id
            )
        except Exception as e:
            return {
                "answer": f"Error procesando documentos: {str(e)}",
                "source_documents": [],
                "chat_history": [],
                "has_documents": True,
                "error": str(e)
            }
        
        # Obtener o crear memoria de conversación
        if not session_id:
            session_id = f"{current_user.id}_{pet_id}"
        
        if session_id not in ChatController._conversation_memories:
            ChatController._conversation_memories[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        
        memory = ChatController._conversation_memories[session_id]
        
        # Hacer pregunta
        try:
            result = langchain_service.ask_question(
                question=question,
                vector_store=vector_store,
                memory=memory
            )
            
            return {
                "answer": result["answer"],
                "source_documents": result["source_documents"],
                "chat_history": result["chat_history"],
                "has_documents": True,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "answer": f"Error procesando la pregunta: {str(e)}",
                "source_documents": [],
                "chat_history": [],
                "has_documents": True,
                "error": str(e)
            }
    
    @staticmethod
    def clear_conversation(session_id: str) -> bool:
        """
        Limpia la memoria de una conversación
        
        Args:
            session_id: ID de sesión
            
        Returns:
            True si se limpió correctamente
        """
        if session_id in ChatController._conversation_memories:
            del ChatController._conversation_memories[session_id]
            return True
        return False
    
    @staticmethod
    def get_conversation_history(session_id: str) -> List[Dict[str, str]]:
        """
        Obtiene el historial de conversación de una sesión
        
        Args:
            session_id: ID de sesión
            
        Returns:
            Lista de mensajes del historial
        """
        if session_id not in ChatController._conversation_memories:
            return []
        
        memory = ChatController._conversation_memories[session_id]
        
        history = []
        try:
            # Intentar acceder al historial de diferentes formas según la versión de LangChain
            if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
                messages = memory.chat_memory.messages
            elif hasattr(memory, 'buffer') and hasattr(memory.buffer, 'messages'):
                messages = memory.buffer.messages
            elif hasattr(memory, 'chat_history'):
                messages = memory.chat_history.messages if hasattr(memory.chat_history, 'messages') else []
            else:
                # Intentar cargar desde variables de memoria
                memory_vars = memory.load_memory_variables({})
                messages = memory_vars.get('chat_history', [])
            
            for msg in messages:
                if hasattr(msg, 'content'):
                    # Determinar el rol del mensaje
                    msg_type = type(msg).__name__
                    if 'Human' in msg_type or 'user' in msg_type.lower():
                        role = "user"
                    elif 'AI' in msg_type or 'assistant' in msg_type.lower() or 'AIMessage' in msg_type:
                        role = "assistant"
                    else:
                        role = "user"  # Por defecto
                    
                    history.append({
                        "role": role,
                        "content": msg.content
                    })
        except Exception as e:
            # Si hay error, retornar lista vacía
            print(f"⚠️ Error extrayendo historial: {str(e)}")
            return []
        
        return history

