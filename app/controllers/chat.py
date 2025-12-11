"""
Controlador para chat con IA veterinaria
Maneja sesiones, memoria conversacional con límite de 6 interacciones
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models import User, Pet
from app.services.langchain_service import LangChainService
from app.controllers.pets import PetController
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage


class ChatController:
    """Controlador para chat veterinario con IA y memoria limitada"""
    
    # Almacenar memorias por sesión (en producción usar Redis)
    _conversation_memories: Dict[str, ConversationBufferMemory] = {}
    
    # Configuración de límites de memoria
    MAX_INTERACTIONS = 6  # Máximo 6 interacciones (pregunta-respuesta)
    MAX_MESSAGES = MAX_INTERACTIONS * 2  # 12 mensajes totales (6 usuario + 6 asistente)
    
    @staticmethod
    def get_pet_by_id(db: Session, pet_id: str, current_user: User) -> Pet:
        """Verifica que mascota existe y pertenece al usuario"""
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
        Hace pregunta sobre mascota usando IA veterinaria con memoria limitada
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            question: Pregunta del usuario
            current_user: Usuario actual
            session_id: ID de sesión para contexto (opcional)
            
        Returns:
            Dict con respuesta, historial y metadata
        """
        # Verificar mascota
        pet = ChatController.get_pet_by_id(db, pet_id, current_user)
        
        # Inicializar servicio
        langchain_service = LangChainService()
        
        # Obtener documentos
        pdf_urls = langchain_service.get_pet_documents_from_db(db, pet_id)
        has_documents = len(pdf_urls) > 0
        
        # Crear vector store solo si hay documentos
        vector_store = None
        use_documents = False
        
        if pdf_urls:
            try:
                print(f"📄 Intentando procesar {len(pdf_urls)} documento(s)...")
                for i, url in enumerate(pdf_urls, 1):
                    print(f"   {i}. {url}")
                
                vector_store = langchain_service.create_vector_store(
                    pdf_urls=pdf_urls,
                    pet_id=pet_id
                )
                use_documents = True
                print(f"✅ RAG activado con {len(pdf_urls)} documentos")
            except Exception as e:
                print(f"❌ Error procesando documentos: {str(e)}")
                import traceback
                print(f"Traceback completo:")
                traceback.print_exc()
                use_documents = False
                # Continuar sin documentos pero informar al usuario
        else:
            print(f"💬 Sin documentos - modo veterinario experto")
        
        # Obtener o crear memoria conversacional
        if not session_id:
            session_id = f"{current_user.id}_{pet_id}"
        
        # Crear memoria si no existe
        if session_id not in ChatController._conversation_memories:
            memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                output_key="answer"
            )
            ChatController._conversation_memories[session_id] = memory
            print(f"🆕 Nueva sesión creada: {session_id}")
        else:
            memory = ChatController._conversation_memories[session_id]
            print(f"📚 Sesión existente: {session_id}")
        
        # Limitar mensajes en memoria ANTES de hacer la pregunta
        ChatController._limit_memory_messages(memory)
        
        # Log historial antes de pregunta
        history_before = ChatController._get_memory_message_count(memory)
        interactions_before = history_before // 2
        print(f"📊 Memoria antes: {interactions_before} interacciones ({history_before} mensajes)")
        
        # Hacer pregunta
        try:
            result = langchain_service.ask_question(
                question=question,
                vector_store=vector_store,
                memory=memory,
                use_documents=use_documents
            )
            
            # Limitar mensajes DESPUÉS de la pregunta también
            ChatController._limit_memory_messages(memory)
            
            # Log historial después de pregunta
            history_after = ChatController._get_memory_message_count(memory)
            interactions_after = history_after // 2
            print(f"📊 Memoria después: {interactions_after} interacciones ({history_after} mensajes)")
            
            # Información de memoria para el usuario
            memory_info = {
                "current_messages": history_after,
                "max_messages": ChatController.MAX_MESSAGES,
                "interactions_count": interactions_after,
                "max_interactions": ChatController.MAX_INTERACTIONS
            }
            
            # Asegurar campos completos
            return {
                "answer": result.get("answer", "No se pudo generar respuesta."),
                "source_documents": result.get("source_documents", []),
                "chat_history": result.get("chat_history", []),
                "has_documents": has_documents,
                "session_id": session_id,
                "memory_info": memory_info,
                "error": result.get("error")
            }
            
        except Exception as e:
            print(f"❌ Error en pregunta: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "answer": f"Lo siento, ocurrió un error: {str(e)}",
                "source_documents": [],
                "chat_history": [],
                "has_documents": has_documents,
                "session_id": session_id,
                "memory_info": {
                    "current_messages": 0,
                    "max_messages": ChatController.MAX_MESSAGES,
                    "interactions_count": 0,
                    "max_interactions": ChatController.MAX_INTERACTIONS
                },
                "error": str(e)
            }
    
    @staticmethod
    def clear_conversation(session_id: str) -> bool:
        """Limpia memoria de una conversación"""
        if session_id in ChatController._conversation_memories:
            del ChatController._conversation_memories[session_id]
            print(f"🗑️ Sesión eliminada: {session_id}")
            return True
        return False
    
    @staticmethod
    def _limit_memory_messages(memory: ConversationBufferMemory):
        """
        Limita mensajes en memoria a MAX_MESSAGES (12 = 6 interacciones)
        Mantiene solo los mensajes más recientes
        """
        try:
            # Cargar mensajes actuales
            memory_vars = memory.load_memory_variables({})
            messages = memory_vars.get('chat_history', [])
            
            if not messages:
                return
            
            current_count = len(messages)
            
            # Si excede el límite, mantener solo los últimos MAX_MESSAGES
            if current_count > ChatController.MAX_MESSAGES:
                messages_to_keep = messages[-ChatController.MAX_MESSAGES:]
                interactions_removed = (current_count - ChatController.MAX_MESSAGES) // 2
                
                print(f"✂️ Limitando memoria: {current_count} -> {ChatController.MAX_MESSAGES} mensajes")
                print(f"   Removidas {interactions_removed} interacciones antiguas")
                
                # Limpiar y restaurar solo los mensajes recientes
                if hasattr(memory, 'chat_memory'):
                    memory.chat_memory.clear()
                    for msg in messages_to_keep:
                        memory.chat_memory.add_message(msg)
                        
        except Exception as e:
            print(f"⚠️ Error limitando memoria: {str(e)}")
    
    @staticmethod
    def _get_memory_message_count(memory: ConversationBufferMemory) -> int:
        """Obtiene conteo de mensajes en memoria"""
        try:
            memory_vars = memory.load_memory_variables({})
            messages = memory_vars.get('chat_history', [])
            return len(messages) if isinstance(messages, list) else 0
        except:
            return 0
    
    @staticmethod
    def get_conversation_history(session_id: str) -> List[Dict[str, str]]:
        """Obtiene historial de conversación de una sesión"""
        if session_id not in ChatController._conversation_memories:
            return []
        
        memory = ChatController._conversation_memories[session_id]
        
        try:
            memory_vars = memory.load_memory_variables({})
            messages = memory_vars.get('chat_history', [])
            
            history = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history.append({"role": "assistant", "content": msg.content})
            
            return history
            
        except Exception as e:
            print(f"⚠️ Error obteniendo historial: {str(e)}")
            return []
    
    @staticmethod
    def get_active_sessions() -> List[str]:
        """Obtiene lista de sesiones activas"""
        return list(ChatController._conversation_memories.keys())
    
    @staticmethod
    def get_session_stats(session_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene estadísticas de una sesión"""
        if session_id not in ChatController._conversation_memories:
            return None
        
        memory = ChatController._conversation_memories[session_id]
        message_count = ChatController._get_memory_message_count(memory)
        interactions_count = message_count // 2
        
        return {
            "session_id": session_id,
            "message_count": message_count,
            "max_messages": ChatController.MAX_MESSAGES,
            "interactions_count": interactions_count,
            "max_interactions": ChatController.MAX_INTERACTIONS,
            "memory_usage": f"{interactions_count}/{ChatController.MAX_INTERACTIONS} interacciones ({message_count}/{ChatController.MAX_MESSAGES} mensajes)"
        }