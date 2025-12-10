"""
Servicio LangChain mejorado para chat veterinario con IA
Incluye manejo robusto de memoria conversacional y modo sin documentos
"""
from typing import List, Optional, Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from app.config import settings
from app.services.s3_service import S3Service
import os
import tempfile
import requests


class LangChainService:
    """Servicio para chat veterinario con IA usando LangChain"""
    
    # Prompt optimizado para veterinario experto
    VETERINARY_SYSTEM_PROMPT = """Eres un veterinario experto altamente calificado con más de 15 años de experiencia en medicina veterinaria. Tu especialización abarca todas las especies de animales domésticos y de compañía.

**TU EXPERIENCIA INCLUYE:**
- Diagnóstico y tratamiento de enfermedades en perros, gatos, aves, roedores, reptiles y otros animales
- Medicina preventiva: vacunación, desparasitación, chequeos de rutina
- Nutrición especializada para diferentes especies y condiciones de salud
- Comportamiento animal y problemas de conducta
- Emergencias veterinarias y primeros auxilios
- Cirugía general y procedimientos médicos
- Geriatría y cuidados paliativos en mascotas

**CÓMO DEBES RESPONDER:**
1. **Profesional pero empático**: Usa lenguaje claro y cercano, sin tecnicismos excesivos
2. **Basado en evidencia**: Proporciona información respaldada por medicina veterinaria moderna
3. **Seguridad primero**: Si detectas una emergencia, recomienda atención veterinaria inmediata
4. **Memoria activa**: SIEMPRE mantén el contexto de la conversación. Si el usuario pregunta sobre algo mencionado antes, haz referencia explícita a esa información
5. **Específico y práctico**: Da recomendaciones concretas y accionables
6. **Honesto sobre limitaciones**: Si algo requiere examen físico o pruebas, indícalo claramente

**IMPORTANTE:**
- Siempre recuerda y haz referencia al historial de la conversación
- Si el usuario pregunta "¿recuerdas lo que te pregunté?" o similar, debes poder responder específicamente
- Mantén un tono cálido pero profesional
- Si no estás seguro de algo, admítelo y recomienda consulta presencial

**LIMITACIONES:**
- No puedes reemplazar una consulta veterinaria presencial
- No puedes recetar medicamentos sin examen físico
- No puedes diagnosticar definitivamente sin pruebas
- Siempre recomienda visita veterinaria ante síntomas graves"""

    def __init__(self):
        """Inicializa el servicio LangChain"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        # Inicializar embeddings para RAG
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Inicializar LLM con temperatura optimizada para veterinario
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # Balance entre creatividad y precisión
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Configurar LangSmith si está habilitado
        if settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        
        self.s3_service = S3Service()
        
        # Text splitter para documentos
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            length_function=len,
        )
    
    def _download_pdf_from_s3(self, s3_url: str) -> str:
        """Descarga un PDF desde S3 a archivo temporal"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            response = requests.get(s3_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
        except Exception as e:
            raise Exception(f"Error descargando PDF: {str(e)}")
    
    def _load_pdf_documents(self, pdf_urls: List[str]) -> List[Document]:
        """Carga y procesa múltiples PDFs"""
        all_documents = []
        
        for pdf_url in pdf_urls:
            try:
                temp_path = self._download_pdf_from_s3(pdf_url)
                
                try:
                    loader = PyPDFLoader(temp_path)
                    documents = loader.load()
                    
                    for doc in documents:
                        doc.metadata['source'] = pdf_url
                        doc.metadata['source_type'] = 'pet_document'
                    
                    all_documents.extend(documents)
                finally:
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
        """Crea vector store para documentos de mascota"""
        if not pdf_urls:
            raise ValueError("No hay PDFs para procesar")
        
        print(f"📄 Cargando {len(pdf_urls)} PDF(s)...")
        documents = self._load_pdf_documents(pdf_urls)
        
        if not documents:
            raise ValueError("No se pudieron cargar documentos")
        
        print(f"✂️ Dividiendo en chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"✅ {len(chunks)} chunks creados")
        
        if not collection_name:
            collection_name = f"pet_{pet_id}_documents"
        
        connection_string = settings.DATABASE_URL
        if connection_string.startswith("postgresql+psycopg2://"):
            connection_string = connection_string.replace(
                "postgresql+psycopg2://", "postgresql+psycopg://", 1
            )
        elif connection_string.startswith("postgresql://"):
            connection_string = connection_string.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        
        print(f"💾 Almacenando embeddings en PostgreSQL...")
        try:
            vector_store = PGVector.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=collection_name,
                connection_string=connection_string,
                pre_delete_collection=False,
            )
            print(f"✅ Embeddings almacenados")
        except Exception as e:
            print(f"⚠️ Recreando colección...")
            try:
                temp_store = PGVector(
                    collection_name=collection_name,
                    connection_string=connection_string,
                    embedding_function=self.embeddings,
                )
                try:
                    temp_store.delete_collection()
                except:
                    pass
            except:
                pass
            
            vector_store = PGVector.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=collection_name,
                connection_string=connection_string,
            )
            print(f"✅ Colección creada")
        
        return vector_store
    
    def ask_question(
        self,
        question: str,
        vector_store: Optional[PGVector] = None,
        memory: Optional[ConversationBufferMemory] = None,
        use_documents: bool = True
    ) -> Dict[str, Any]:
        """
        Hace una pregunta al veterinario experto con memoria conversacional
        
        Args:
            question: Pregunta del usuario
            vector_store: Vector store con documentos (opcional)
            memory: Memoria conversacional
            use_documents: Si usar RAG o modo conversación general
            
        Returns:
            Dict con respuesta, historial y documentos fuente
        """
        print(f"❓ Procesando: {question[:100]}...")
        
        # Crear memoria si no existe
        if memory is None:
            memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                output_key="answer"
            )
        
        try:
            # Modo con documentos (RAG)
            if use_documents and vector_store is not None:
                answer, source_docs = self._ask_with_rag(
                    question, vector_store, memory
                )
            # Modo sin documentos (conversación general)
            else:
                answer, source_docs = self._ask_without_documents(
                    question, memory
                )
            
            # Extraer historial actualizado
            chat_history = self._extract_chat_history(memory)
            
            # Formatear documentos fuente
            formatted_docs = self._format_source_documents(source_docs)
            
            return {
                "answer": answer,
                "source_documents": formatted_docs,
                "chat_history": chat_history,
                "has_documents": use_documents and vector_store is not None,
                "error": None
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "answer": f"Lo siento, ocurrió un error al procesar tu pregunta. Por favor, inténtalo nuevamente.",
                "source_documents": [],
                "chat_history": self._extract_chat_history(memory) if memory else [],
                "has_documents": False,
                "error": str(e)
            }
    
    def _ask_with_rag(
        self,
        question: str,
        vector_store: PGVector,
        memory: ConversationBufferMemory
    ) -> tuple[str, List]:
        """Pregunta usando RAG (con documentos)"""
        print("📚 Modo RAG activado")
        
        retriever = vector_store.as_retriever(
            search_kwargs={"k": settings.RAG_TOP_K_RESULTS}
        )
        
        # Prompt que combina documentos con conocimiento veterinario
        qa_prompt = PromptTemplate(
            template=f"""{self.VETERINARY_SYSTEM_PROMPT}

**DOCUMENTOS DE LA MASCOTA:**
{{context}}

**HISTORIAL DE CONVERSACIÓN:**
Recuerda todo lo que hemos hablado anteriormente y haz referencia a ello cuando sea relevante.

**PREGUNTA ACTUAL:**
{{question}}

**TU RESPUESTA COMO VETERINARIO EXPERTO:**""",
            input_variables=["context", "question"]
        )
        
        # Crear cadena conversacional
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=False,
            combine_docs_chain_kwargs={"prompt": qa_prompt}
        )
        
        result = chain.invoke({"question": question})
        answer = result.get("answer", "")
        source_docs = result.get("source_documents", [])
        
        return answer, source_docs
    
    def _ask_without_documents(
        self,
        question: str,
        memory: ConversationBufferMemory
    ) -> tuple[str, List]:
        """Pregunta sin documentos (conversación general)"""
        print("💬 Modo conversación general")
        
        # Cargar historial de memoria
        memory_vars = memory.load_memory_variables({})
        history = memory_vars.get('chat_history', [])
        
        # Construir mensajes para el LLM
        messages = [
            SystemMessage(content=self.VETERINARY_SYSTEM_PROMPT)
        ]
        
        # Agregar historial
        if isinstance(history, list):
            messages.extend(history)
        
        # Agregar pregunta actual
        messages.append(HumanMessage(content=question))
        
        # Invocar LLM
        response = self.llm.invoke(messages)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        # Guardar en memoria
        memory.save_context(
            {"question": question},
            {"answer": answer}
        )
        
        return answer, []
    
    def _extract_chat_history(self, memory: ConversationBufferMemory) -> List[Dict[str, str]]:
        """Extrae historial de conversación de forma robusta"""
        history = []
        
        try:
            memory_vars = memory.load_memory_variables({})
            chat_history = memory_vars.get('chat_history', [])
            
            if isinstance(chat_history, list):
                for msg in chat_history:
                    if isinstance(msg, BaseMessage):
                        # Determinar rol
                        if isinstance(msg, HumanMessage):
                            role = "user"
                        elif isinstance(msg, AIMessage):
                            role = "assistant"
                        else:
                            role = "user"
                        
                        history.append({
                            "role": role,
                            "content": msg.content
                        })
        except Exception as e:
            print(f"⚠️ Error extrayendo historial: {str(e)}")
        
        return history
    
    def _format_source_documents(self, source_docs: List) -> List[Dict[str, Any]]:
        """Formatea documentos fuente para la respuesta"""
        formatted = []
        
        for doc in source_docs:
            try:
                content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                formatted.append({
                    "content": content,
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", 0)
                })
            except Exception as e:
                print(f"⚠️ Error formateando documento: {str(e)}")
                continue
        
        return formatted
    
    def get_pet_documents_from_db(self, db, pet_id: str) -> List[str]:
        """Obtiene URLs de documentos PDF de mascota desde DB"""
        from app.models import PetPhoto
        import uuid
        
        try:
            pet_uuid = uuid.UUID(pet_id) if isinstance(pet_id, str) else pet_id
        except (ValueError, AttributeError):
            pet_uuid = pet_id
        
        print(f"🔍 Buscando documentos para mascota: {pet_id}")
        
        documents = db.query(PetPhoto).filter(
            PetPhoto.pet_id == pet_uuid,
            PetPhoto.file_type == "document"
        ).all()
        
        urls = [doc.url for doc in documents if doc.url]
        print(f"📄 {len(urls)} documentos encontrados")
        
        return urls