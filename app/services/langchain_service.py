"""
Servicio LangChain para RAG (Retrieval Augmented Generation)
Procesa PDFs de mascotas y permite hacer preguntas con contexto conversacional
"""
import os
import tempfile
import requests
from typing import List, Optional, Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from app.config import settings
from app.services.s3_service import S3Service

class LangChainService:
    """Servicio para procesamiento de documentos con LangChain y RAG"""
    
    def __init__(self):
        """Inicializa el servicio LangChain"""
        # Configurar OpenAI
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada en el .env")
        
        # Inicializar embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Inicializar LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Configurar LangSmith si está habilitado
        if settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        
        # Servicio S3 para descargar PDFs
        self.s3_service = S3Service()
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            length_function=len,
        )
    
    def _download_pdf_from_s3(self, s3_url: str) -> str:
        """
        Descarga un PDF desde S3 a un archivo temporal
        
        Args:
            s3_url: URL del PDF en S3
            
        Returns:
            Ruta al archivo temporal descargado
        """
        try:
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            # Descargar desde S3
            response = requests.get(s3_url, stream=True)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
        except Exception as e:
            raise Exception(f"Error descargando PDF desde S3: {str(e)}")
    
    def _load_pdf_documents(self, pdf_urls: List[str]) -> List[Document]:
        """
        Carga y procesa múltiples PDFs desde URLs de S3
        
        Args:
            pdf_urls: Lista de URLs de PDFs en S3
            
        Returns:
            Lista de documentos procesados
        """
        all_documents = []
        
        for pdf_url in pdf_urls:
            try:
                # Descargar PDF temporalmente
                temp_path = self._download_pdf_from_s3(pdf_url)
                
                try:
                    # Cargar PDF
                    loader = PyPDFLoader(temp_path)
                    documents = loader.load()
                    
                    # Agregar metadata sobre el origen
                    for doc in documents:
                        doc.metadata['source'] = pdf_url
                        doc.metadata['source_type'] = 'pet_document'
                    
                    all_documents.extend(documents)
                finally:
                    # Eliminar archivo temporal
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        
            except Exception as e:
                print(f"⚠️ Error procesando PDF {pdf_url}: {str(e)}")
                continue
        
        return all_documents
    
    def create_vector_store(
        self, 
        pdf_urls: List[str], 
        pet_id: str,
        collection_name: Optional[str] = None
    ) -> PGVector:
        """
        Crea o actualiza un vector store para los documentos de una mascota
        
        Args:
            pdf_urls: Lista de URLs de PDFs en S3
            pet_id: ID de la mascota
            collection_name: Nombre de la colección (opcional)
            
        Returns:
            Instancia de PGVector
        """
        if not pdf_urls:
            raise ValueError("No hay PDFs para procesar")
        
        # Cargar documentos
        print(f"📄 Cargando {len(pdf_urls)} PDF(s) para la mascota {pet_id}...")
        for i, url in enumerate(pdf_urls, 1):
            print(f"   [{i}/{len(pdf_urls)}] {url}")
        documents = self._load_pdf_documents(pdf_urls)
        
        if not documents:
            raise ValueError("No se pudieron cargar documentos de los PDFs")
        
        print(f"✅ Cargados {len(documents)} documentos (páginas totales)")
        total_chars = sum(len(doc.page_content) for doc in documents)
        print(f"   Total de caracteres: {total_chars:,}")
        
        # Dividir en chunks
        print(f"✂️ Dividiendo documentos en chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"✅ Creados {len(chunks)} chunks")
        if chunks:
            avg_chunk_size = sum(len(chunk.page_content) for chunk in chunks) / len(chunks)
            print(f"   Tamaño promedio de chunk: {avg_chunk_size:.0f} caracteres")
        
        # Crear nombre de colección único por mascota
        if not collection_name:
            collection_name = f"pet_{pet_id}_documents"
        
        # Obtener connection string de PostgreSQL
        connection_string = settings.DATABASE_URL
        
        # Convertir postgresql+psycopg2:// a postgresql+psycopg:// para pgvector
        if connection_string.startswith("postgresql+psycopg2://"):
            connection_string = connection_string.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
        elif connection_string.startswith("postgresql://"):
            connection_string = connection_string.replace("postgresql://", "postgresql+psycopg://", 1)
        
        # Crear o actualizar vector store
        # Nota: PGVector.from_documents crea la colección si no existe, o la actualiza si existe
        print(f"💾 Almacenando embeddings en PostgreSQL...")
        try:
            vector_store = PGVector.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=collection_name,
                connection_string=connection_string,
                pre_delete_collection=False,  # No eliminar, solo agregar/actualizar
            )
            print(f"✅ Embeddings almacenados correctamente")
        except Exception as e:
            # Si falla, intentar eliminar y recrear
            print(f"⚠️ Error al actualizar colección, recreando...")
            try:
                # Eliminar colección existente
                temp_store = PGVector(
                    collection_name=collection_name,
                    connection_string=connection_string,
                    embedding_function=self.embeddings,
                )
                # Intentar eliminar (puede fallar si no existe, está bien)
                try:
                    temp_store.delete_collection()
                except:
                    pass
            except:
                pass
            
            # Crear nueva colección
            vector_store = PGVector.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=collection_name,
                connection_string=connection_string,
            )
            print(f"✅ Colección creada correctamente")
        
        return vector_store
    
    def create_conversation_chain(
        self,
        vector_store: PGVector,
        memory: Optional[ConversationBufferMemory] = None
    ) -> ConversationalRetrievalChain:
        """
        Crea una cadena conversacional con RAG
        
        Args:
            vector_store: Vector store con los documentos
            memory: Memoria conversacional (opcional)
            
        Returns:
            Cadena conversacional configurada
        """
        # Crear memoria si no se proporciona
        if memory is None:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        
        # Crear retriever
        retriever = vector_store.as_retriever(
            search_kwargs={"k": settings.RAG_TOP_K_RESULTS}
        )
        
        # Prompt personalizado que incluye historial de conversación
        # Este prompt se usa para combinar documentos, pero ConversationalRetrievalChain
        # maneja el historial automáticamente a través de la memoria
        qa_prompt = PromptTemplate(
            template="""Eres un asistente veterinario especializado en el cuidado de mascotas. 
Tu trabajo es responder preguntas sobre la salud y el historial médico de las mascotas basándote ÚNICAMENTE en los documentos proporcionados.

IMPORTANTE:
- Responde SOLO basándote en la información contenida en los siguientes fragmentos de documentos
- Si la información no está en los documentos, di claramente "No encontré esa información en los documentos de la mascota"
- Sé específico y menciona fechas, medicamentos, tratamientos, vacunaciones, etc. cuando estén disponibles en los documentos
- Si no sabes la respuesta basándote en los documentos, di que no encontraste esa información
- Puedes hacer referencia a preguntas y respuestas anteriores de esta conversación si es relevante

Fragmentos de documentos relevantes:
{context}

Pregunta: {question}

Respuesta basada únicamente en los documentos:""",
            input_variables=["context", "question"]
        )
        
        # Crear cadena conversacional con prompt personalizado
        # ConversationalRetrievalChain maneja automáticamente la memoria
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt}
        )
        
        return chain
    
    def ask_question(
        self,
        question: str,
        vector_store: PGVector,
        memory: Optional[ConversationBufferMemory] = None
    ) -> Dict[str, Any]:
        """
        Hace una pregunta sobre los documentos usando RAG
        
        Args:
            question: Pregunta del usuario
            vector_store: Vector store con los documentos
            memory: Memoria conversacional (opcional)
            
        Returns:
            Dict con la respuesta y documentos fuente
        """
        # Verificar que hay documentos en el vector store antes de hacer la pregunta
        print(f"🔍 Verificando vector store...")
        try:
            # Hacer una búsqueda de prueba para verificar que hay documentos
            test_docs = vector_store.similarity_search("test", k=1)
            print(f"✅ Vector store tiene documentos: {len(test_docs)} documentos encontrados en búsqueda de prueba")
        except Exception as e:
            print(f"⚠️ Error verificando vector store (continuando de todas formas): {str(e)}")
            # No lanzar la excepción, solo loguear - puede que el vector store esté vacío pero aún así podemos intentar
        
        # Crear cadena conversacional
        chain = self.create_conversation_chain(vector_store, memory)
        
        # Hacer pregunta
        print(f"❓ Procesando pregunta: {question}")
        print(f"🔍 Buscando en {settings.RAG_TOP_K_RESULTS} documentos más relevantes...")
        
        # Verificar historial antes de la pregunta
        if memory:
            history_before = self._extract_chat_history(memory)
            print(f"📚 Historial antes de la pregunta: {len(history_before)} mensajes")
            if history_before:
                print(f"📝 Último mensaje del historial: {history_before[-1]}")
        
        # ConversationalRetrievalChain debería actualizar la memoria automáticamente
        try:
            result = chain.invoke({"question": question})
            print(f"✅ Respuesta generada: {result.get('answer', '')[:100] if result.get('answer') else 'Sin respuesta'}...")
        except Exception as e:
            print(f"❌ Error invocando la cadena: {str(e)}")
            import traceback
            traceback.print_exc()
            raise  # Re-lanzar para que el controlador lo maneje
        
        # Obtener documentos fuente
        source_docs = result.get("source_documents", [])
        print(f"📄 Documentos fuente encontrados: {len(source_docs)}")
        
        # Verificar historial después de la pregunta
        if memory:
            history_after = self._extract_chat_history(memory)
            print(f"📚 Historial después de la pregunta: {len(history_after)} mensajes")
            if history_after:
                print(f"📝 Últimos 2 mensajes del historial:")
                for msg in history_after[-2:]:
                    print(f"   - {msg['role']}: {msg['content'][:50]}...")
            else:
                print(f"⚠️ ADVERTENCIA: El historial está vacío después de la pregunta")
                # Intentar debug: ver qué tiene la memoria
                try:
                    if hasattr(memory, 'chat_memory'):
                        print(f"   Debug - chat_memory.messages: {len(memory.chat_memory.messages) if hasattr(memory.chat_memory, 'messages') else 'N/A'}")
                    memory_vars = memory.load_memory_variables({})
                    print(f"   Debug - memory_vars keys: {list(memory_vars.keys())}")
                    print(f"   Debug - chat_history type: {type(memory_vars.get('chat_history', None))}")
                except Exception as e:
                    print(f"   Debug error: {str(e)}")
        
        # Asegurar que answer no sea None
        answer = result.get("answer", "")
        if not answer:
            answer = "No se pudo generar una respuesta."
        
        # Formatear documentos fuente
        formatted_source_docs = []
        for doc in source_docs:
            try:
                content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                formatted_source_docs.append({
                    "content": content,
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", 0)
                })
            except Exception as e:
                print(f"⚠️ Error formateando documento fuente: {str(e)}")
                continue
        
        # Extraer historial de conversación
        chat_history = []
        if memory:
            try:
                chat_history = self._extract_chat_history(memory)
            except Exception as e:
                print(f"⚠️ Error extrayendo historial: {str(e)}")
                chat_history = []
        
        return {
            "answer": answer,
            "source_documents": formatted_source_docs,
            "chat_history": chat_history
        }
    
    def _extract_chat_history(self, memory: ConversationBufferMemory) -> List[Dict[str, str]]:
        """
        Extrae el historial de conversación de la memoria
        
        Args:
            memory: Memoria conversacional
            
        Returns:
            Lista de mensajes del historial
        """
        history = []
        try:
            # Método más confiable: usar load_memory_variables primero
            memory_vars = memory.load_memory_variables({})
            chat_history = memory_vars.get('chat_history', [])
            
            # Si chat_history es una lista de mensajes
            if isinstance(chat_history, list) and len(chat_history) > 0:
                messages = chat_history
            # Si chat_history es un string (formato antiguo), intentar parsearlo
            elif isinstance(chat_history, str) and chat_history.strip():
                # Intentar acceder directamente a los mensajes
                if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
                    messages = memory.chat_memory.messages
                elif hasattr(memory, 'buffer') and hasattr(memory.buffer, 'messages'):
                    messages = memory.buffer.messages
                else:
                    messages = []
            else:
                # Intentar acceder directamente a los mensajes
                if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
                    messages = memory.chat_memory.messages
                elif hasattr(memory, 'buffer') and hasattr(memory.buffer, 'messages'):
                    messages = memory.buffer.messages
                elif hasattr(memory, 'chat_history'):
                    messages = memory.chat_history.messages if hasattr(memory.chat_history, 'messages') else []
                else:
                    messages = []
            
            # Procesar mensajes
            for msg in messages:
                if hasattr(msg, 'content'):
                    # Determinar el rol del mensaje
                    msg_type = type(msg).__name__
                    if 'Human' in msg_type or 'user' in msg_type.lower() or 'HumanMessage' in msg_type:
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
            import traceback
            traceback.print_exc()
            return []
        
        return history
    
    def get_pet_documents_from_db(
        self,
        db,
        pet_id: str
    ) -> List[str]:
        """
        Obtiene las URLs de los documentos PDF de una mascota desde la base de datos
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota (puede ser string UUID)
            
        Returns:
            Lista de URLs de PDFs
        """
        from app.models import PetPhoto
        import uuid
        
        # Convertir pet_id a UUID si es string
        try:
            if isinstance(pet_id, str):
                pet_uuid = uuid.UUID(pet_id)
            else:
                pet_uuid = pet_id
        except (ValueError, AttributeError) as e:
            # Si no es un UUID válido, intentar buscar como string
            print(f"⚠️ Error convirtiendo pet_id a UUID: {str(e)}, usando como string")
            pet_uuid = pet_id
        
        print(f"🔍 Buscando documentos para mascota: {pet_id} (UUID: {pet_uuid})")
        
        documents = db.query(PetPhoto).filter(
            PetPhoto.pet_id == pet_uuid,
            PetPhoto.file_type == "document"
        ).all()
        
        print(f"📋 Encontrados {len(documents)} registros en la base de datos")
        
        urls = [doc.url for doc in documents if doc.url]
        print(f"📄 URLs válidas encontradas: {len(urls)}")
        for i, url in enumerate(urls, 1):
            print(f"   {i}. {url}")
        
        if not urls:
            print(f"⚠️ No se encontraron URLs válidas para la mascota {pet_id}")
        
        return urls

