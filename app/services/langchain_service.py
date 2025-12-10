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
        documents = self._load_pdf_documents(pdf_urls)
        
        if not documents:
            raise ValueError("No se pudieron cargar documentos de los PDFs")
        
        # Dividir en chunks
        print(f"✂️ Dividiendo documentos en chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"✅ Creados {len(chunks)} chunks")
        
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
        
        # Crear cadena conversacional
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True
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
        # Crear cadena conversacional
        chain = self.create_conversation_chain(vector_store, memory)
        
        # Hacer pregunta
        result = chain.invoke({"question": question})
        
        return {
            "answer": result.get("answer", ""),
            "source_documents": [
                {
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", 0)
                }
                for doc in result.get("source_documents", [])
            ],
            "chat_history": self._extract_chat_history(memory) if memory else []
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
    
    def get_pet_documents_from_db(
        self,
        db,
        pet_id: str
    ) -> List[str]:
        """
        Obtiene las URLs de los documentos PDF de una mascota desde la base de datos
        
        Args:
            db: Sesión de base de datos
            pet_id: ID de la mascota
            
        Returns:
            Lista de URLs de PDFs
        """
        from app.models import PetPhoto
        
        documents = db.query(PetPhoto).filter(
            PetPhoto.pet_id == pet_id,
            PetPhoto.file_type == "document"
        ).all()
        
        return [doc.url for doc in documents if doc.url]

