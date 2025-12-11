# 🧠 Guía Técnica Detallada: Sistema de Chat con IA Veterinario

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Flujo de Datos Completo](#flujo-de-datos-completo)
3. [Componentes Principales](#componentes-principales)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Alternativas Tecnológicas](#alternativas-tecnológicas)
6. [Enfoques de Implementación](#enfoques-de-implementación)
7. [Memoria Conversacional](#memoria-conversacional)
8. [RAG (Retrieval Augmented Generation)](#rag-retrieval-augmented-generation)
9. [Optimizaciones y Mejores Prácticas](#optimizaciones-y-mejores-prácticas)

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Frontend)                       │
│  - React/Next.js                                                │
│  - Hace peticiones HTTP a la API                                 │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              │ HTTP Request
                              │ POST /chat/pets/{pet_id}/ask
                              │ Headers: Authorization: Bearer <token>
                              │ Body: { question, session_id }
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI (app/routes/chat.py)                  │
│  - Valida autenticación                                          │
│  - Valida esquemas Pydantic                                      │
│  - Maneja errores HTTP                                           │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              │ Llama a ChatController
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CONTROLADOR (app/controllers/chat.py)               │
│  - Gestiona sesiones de conversación                             │
│  - Maneja memoria conversacional                                 │
│  - Limita memoria a 6 interacciones (12 mensajes)               │
│  - Obtiene documentos de la mascota                              │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              │ Crea/Usa LangChainService
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│          SERVICIO LANGCHAIN (app/services/langchain_service.py)  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Carga Documentos PDF desde S3                         │   │
│  │    - PyPDFLoader descarga y procesa PDFs                 │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                           │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │ 2. Divide en Chunks                                      │   │
│  │    - RecursiveCharacterTextSplitter                      │   │
│  │    - Chunk size: 1000 caracteres                         │   │
│  │    - Overlap: 200 caracteres                             │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                           │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │ 3. Genera Embeddings                                     │   │
│  │    - OpenAIEmbeddings (text-embedding-3-small)          │   │
│  │    - Convierte texto a vectores de 1536 dimensiones     │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                           │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │ 4. Almacena en Vector Store                              │   │
│  │    - PGVector (PostgreSQL + pgvector extension)          │   │
│  │    - Búsqueda por similitud semántica                    │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                           │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │ 5. Crea Cadena Conversacional                            │   │
│  │    - ConversationalRetrievalChain (con documentos)        │   │
│  │    - SimpleConversationChain (sin documentos)             │   │
│  │    - ConversationBufferMemory para historial              │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                           │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │ 6. Invoca LLM                                            │   │
│  │    - ChatOpenAI (gpt-4o-mini)                            │   │
│  │    - Recibe: pregunta + historial + documentos          │   │
│  │    - Retorna: respuesta generada                         │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         │ Respuesta
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPUESTA AL CLIENTE                          │
│  {                                                               │
│    "answer": "Respuesta del veterinario...",                    │
│    "source_documents": [...],                                    │
│    "chat_history": [...],                                        │
│    "session_id": "...",                                          │
│    "memory_info": {...}                                          │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos Completo

### Paso 1: Cliente hace petición

```http
POST /chat/pets/876835fa-6c7d-4c97-bc18-4e5728e8bc13/ask
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "question": "¿Puedes leer el documento de vacunación de mi mascota?",
  "session_id": "user123_pet456"
}
```

### Paso 2: FastAPI valida y enruta

**Archivo:** `app/routes/chat.py`

```python
@router.post("/pets/{pet_id}/ask")
async def ask_veterinary_question(
    pet_id: str,
    request: ChatQuestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 1. Valida autenticación (get_current_active_user)
    # 2. Valida esquema (ChatQuestionRequest)
    # 3. Llama al controlador
    result = ChatController.ask_question_about_pet(...)
    return ChatResponse(**result)
```

**Validaciones:**
- ✅ Token JWT válido
- ✅ Usuario activo
- ✅ Esquema Pydantic válido
- ✅ Manejo de errores HTTP

### Paso 3: Controlador gestiona la lógica

**Archivo:** `app/controllers/chat.py`

```python
def ask_question_about_pet(...):
    # 1. Verifica que la mascota existe y pertenece al usuario
    pet = ChatController.get_pet_by_id(db, pet_id, current_user)
    
    # 2. Inicializa servicio LangChain
    langchain_service = LangChainService()
    
    # 3. Obtiene documentos PDF de la mascota desde la BD
    pdf_urls = langchain_service.get_pet_documents_from_db(db, pet_id)
    
    # 4. Crea vector store si hay documentos
    if pdf_urls:
        vector_store = langchain_service.create_vector_store(pdf_urls, pet_id)
        use_documents = True
    else:
        vector_store = None
        use_documents = False
    
    # 5. Obtiene o crea memoria conversacional
    if session_id not in ChatController._conversation_memories:
        memory = ConversationBufferMemory(...)
        ChatController._conversation_memories[session_id] = memory
    else:
        memory = ChatController._conversation_memories[session_id]
    
    # 6. Limita memoria a 6 interacciones (12 mensajes)
    ChatController._limit_memory_messages(memory)
    
    # 7. Hace la pregunta usando LangChain
    result = langchain_service.ask_question(
        question=question,
        vector_store=vector_store,
        memory=memory,
        use_documents=use_documents
    )
    
    # 8. Retorna respuesta formateada
    return {
        "answer": result["answer"],
        "source_documents": result["source_documents"],
        "chat_history": result["chat_history"],
        "session_id": session_id,
        "memory_info": {...}
    }
```

### Paso 4: Servicio LangChain procesa

**Archivo:** `app/services/langchain_service.py`

#### 4.1. Si hay documentos (RAG):

```python
def ask_question(question, vector_store, memory, use_documents=True):
    # 1. Crea cadena conversacional con RAG
    chain = ConversationalRetrievalChain.from_llm(
        llm=self.llm,                    # ChatOpenAI
        retriever=vector_store.as_retriever(k=4),  # Top 4 documentos
        memory=memory,                     # ConversationBufferMemory
        return_source_documents=True
    )
    
    # 2. Invoca la cadena
    result = chain.invoke({"question": question})
    
    # 3. Extrae respuesta y documentos
    answer = result["answer"]
    source_docs = result["source_documents"]
    
    return {"answer": answer, "source_documents": source_docs, ...}
```

**Flujo interno de ConversationalRetrievalChain:**

```
1. Recibe pregunta: "¿Cuándo fue la última vacunación?"
2. Obtiene historial de memoria: [mensajes anteriores]
3. Busca documentos relevantes en vector store:
   - Convierte pregunta a embedding
   - Busca top 4 chunks más similares
   - Recupera: "Vacunación aplicada el 17/01/2019..."
4. Construye prompt con:
   - System prompt (instrucciones de veterinario)
   - Historial de conversación
   - Documentos relevantes
   - Pregunta actual
5. Envía a OpenAI GPT-4o-mini
6. Recibe respuesta generada
7. Guarda pregunta y respuesta en memoria
8. Retorna respuesta + documentos fuente
```

#### 4.2. Si NO hay documentos (conversación general):

```python
def ask_question(question, vector_store=None, memory, use_documents=False):
    # 1. Crea cadena conversacional simple
    class SimpleConversationChain:
        def invoke(self, inputs):
            # Obtiene historial de memoria
            memory_vars = memory.load_memory_variables({})
            history = memory_vars.get('chat_history', [])
            
            # Construye mensajes
            messages = [
                SystemMessage(content=VETERINARY_SYSTEM_PROMPT),
                *history,  # Historial previo
                HumanMessage(content=inputs["input"])  # Pregunta actual
            ]
            
            # Invoca LLM directamente
            response = self.llm.invoke(messages)
            answer = response.content
            
            # Guarda en memoria
            memory.save_context(
                {"input": inputs["input"]},
                {"output": answer}
            )
            
            return {"response": answer}
    
    chain = SimpleConversationChain(...)
    result = chain.invoke({"input": question})
    return {"answer": result["response"], ...}
```

### Paso 5: Procesamiento de Documentos (RAG)

Cuando hay documentos PDF, el sistema:

#### 5.1. Descarga PDFs desde S3

```python
def _download_pdf_from_s3(s3_url: str) -> str:
    # 1. Crea archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    # 2. Descarga desde S3 usando requests
    response = requests.get(s3_url, stream=True)
    
    # 3. Guarda en archivo temporal
    with open(temp_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return temp_path
```

#### 5.2. Carga y procesa PDFs

```python
def _load_pdf_documents(pdf_urls: List[str]) -> List[Document]:
    all_documents = []
    
    for pdf_url in pdf_urls:
        # Descarga PDF
        temp_path = self._download_pdf_from_s3(pdf_url)
        
        # Carga con PyPDFLoader
        loader = PyPDFLoader(temp_path)
        documents = loader.load()  # Lista de Document (una por página)
        
        # Agrega metadata
        for doc in documents:
            doc.metadata['source'] = pdf_url
            doc.metadata['source_type'] = 'pet_document'
        
        all_documents.extend(documents)
        
        # Limpia archivo temporal
        os.unlink(temp_path)
    
    return all_documents
```

#### 5.3. Divide en Chunks

```python
# RecursiveCharacterTextSplitter divide el texto en fragmentos
chunks = self.text_splitter.split_documents(documents)

# Ejemplo:
# Documento original: 5000 caracteres
# Chunks creados:
#   - Chunk 1: caracteres 0-1000
#   - Chunk 2: caracteres 800-1800  (200 de overlap)
#   - Chunk 3: caracteres 1600-2600
#   - ...
```

**¿Por qué dividir en chunks?**
- Los LLMs tienen límite de tokens por contexto
- Permite buscar solo las partes relevantes
- Mejora la precisión de la búsqueda semántica

#### 5.4. Genera Embeddings

```python
# OpenAIEmbeddings convierte texto a vectores
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Para cada chunk:
vector = embeddings.embed_query("Vacunación aplicada el 17/01/2019...")
# Resultado: array de 1536 números (dimensiones)

# Ejemplo de vector (simplificado):
# [0.123, -0.456, 0.789, ..., 0.234]  # 1536 números
```

**¿Qué son los embeddings?**
- Representación numérica del significado del texto
- Textos similares tienen vectores similares
- Permite búsqueda semántica (no solo palabras clave)

#### 5.5. Almacena en Vector Store

```python
# PGVector almacena vectores en PostgreSQL
vector_store = PGVector.from_documents(
    documents=chunks,
    embedding=self.embeddings,
    collection_name=f"pet_{pet_id}_documents",
    connection_string=connection_string
)

# Estructura en PostgreSQL:
# Tabla: langchain_pg_embedding
# Columnas:
#   - uuid: ID del chunk
#   - collection_id: ID de la colección
#   - embedding: vector(1536)  # Vector de 1536 dimensiones
#   - document: JSON con metadata y contenido
#   - cmetadata: Metadata adicional
```

**Búsqueda por similitud:**
```sql
-- Cuando se busca "vacunación"
SELECT document, embedding
FROM langchain_pg_embedding
WHERE collection_id = 'pet_123_documents'
ORDER BY embedding <-> '[vector de la pregunta]'  -- Distancia coseno
LIMIT 4;
```

### Paso 6: Generación de Respuesta

#### 6.1. Con RAG (Retrieval Augmented Generation)

```python
# Prompt construido automáticamente por ConversationalRetrievalChain
prompt = f"""
Eres un veterinario experto...

Historial de conversación:
{chat_history}

Documentos relevantes:
{context}  # Top 4 chunks más similares

Pregunta: {question}

Respuesta:
"""

# Se envía a OpenAI
response = llm.invoke(prompt)
```

#### 6.2. Sin documentos (conversación general)

```python
# Mensajes estructurados
messages = [
    SystemMessage(content="Eres un veterinario experto..."),
    HumanMessage(content="Pregunta anterior 1"),
    AIMessage(content="Respuesta anterior 1"),
    HumanMessage(content="Pregunta actual")
]

# Se envía a OpenAI Chat API
response = llm.invoke(messages)
```

### Paso 7: Actualización de Memoria

```python
# Después de recibir respuesta
memory.save_context(
    {"input": question},
    {"output": answer}
)

# La memoria ahora contiene:
# chat_history = [
#     HumanMessage(content="Pregunta 1"),
#     AIMessage(content="Respuesta 1"),
#     HumanMessage(content="Pregunta 2"),
#     AIMessage(content="Respuesta 2"),
#     HumanMessage(content="Pregunta actual"),
#     AIMessage(content="Respuesta actual")
# ]
```

### Paso 8: Limitación de Memoria

```python
def _limit_memory_messages(memory):
    # Obtiene todos los mensajes
    memory_vars = memory.load_memory_variables({})
    messages = memory_vars.get('chat_history', [])
    
    # Si excede 12 mensajes (6 interacciones)
    if len(messages) > 12:
        # Mantiene solo los últimos 12
        messages_to_keep = messages[-12:]
        
        # Limpia y restaura
        memory.chat_memory.clear()
        for msg in messages_to_keep:
            memory.chat_memory.add_message(msg)
```

---

## 🧩 Componentes Principales

### 1. Endpoints (app/routes/chat.py)

#### `POST /chat/pets/{pet_id}/ask`
- **Propósito:** Hacer preguntas al veterinario IA
- **Autenticación:** Requerida (JWT)
- **Input:** `{ question, session_id? }`
- **Output:** `{ answer, source_documents, chat_history, session_id, memory_info }`

#### `GET /chat/sessions/{session_id}/history`
- **Propósito:** Obtener historial completo de una conversación
- **Autenticación:** Requerida
- **Output:** `{ session_id, history, message_count }`

#### `DELETE /chat/sessions/{session_id}`
- **Propósito:** Limpiar memoria de una conversión
- **Autenticación:** Requerida
- **Output:** `{ message, session_id, status }`

#### `GET /chat/sessions`
- **Propósito:** Listar todas las sesiones activas
- **Autenticación:** Requerida
- **Output:** `{ active_sessions, total_count }`

#### `GET /chat/sessions/{session_id}/stats`
- **Propósito:** Obtener estadísticas de uso de memoria
- **Autenticación:** Requerida
- **Output:** `{ session_id, message_count, max_messages, interactions_count, ... }`

---

### 2. Controlador (app/controllers/chat.py)

**Responsabilidades:**
- ✅ Validar que la mascota existe y pertenece al usuario
- ✅ Gestionar sesiones de conversación (crear, obtener, limpiar)
- ✅ Gestionar memoria conversacional (limitar a 6 interacciones)
- ✅ Coordinar entre rutas y servicios
- ✅ Formatear respuestas

**Almacenamiento de Memoria:**
```python
# En memoria (actual - no persistente)
_conversation_memories: Dict[str, ConversationBufferMemory] = {}

# En producción debería usar:
# - Redis (recomendado)
# - PostgreSQL (tabla de conversaciones)
# - MongoDB (colección de mensajes)
```

---

### 3. Servicio LangChain (app/services/langchain_service.py)

**Responsabilidades:**
- ✅ Cargar y procesar documentos PDF
- ✅ Crear y gestionar vector stores
- ✅ Generar embeddings
- ✅ Crear cadenas conversacionales (con y sin RAG)
- ✅ Invocar LLM
- ✅ Extraer historial de conversación

**Clases y Métodos Principales:**

```python
class LangChainService:
    def __init__(self):
        # Inicializa embeddings y LLM
        self.embeddings = OpenAIEmbeddings(...)
        self.llm = ChatOpenAI(...)
        self.text_splitter = RecursiveCharacterTextSplitter(...)
    
    def get_pet_documents_from_db(self, db, pet_id):
        # Obtiene URLs de PDFs desde PostgreSQL
        # Retorna: List[str] de URLs S3
    
    def _download_pdf_from_s3(self, s3_url):
        # Descarga PDF desde S3 a archivo temporal
        # Retorna: str (ruta al archivo temporal)
    
    def _load_pdf_documents(self, pdf_urls):
        # Carga PDFs usando PyPDFLoader
        # Retorna: List[Document]
    
    def create_vector_store(self, pdf_urls, pet_id):
        # 1. Carga documentos
        # 2. Divide en chunks
        # 3. Genera embeddings
        # 4. Almacena en PGVector
        # Retorna: PGVector
    
    def ask_question(self, question, vector_store, memory, use_documents):
        # Decide si usar RAG o conversación general
        # Invoca la cadena apropiada
        # Retorna: Dict con respuesta y metadata
    
    def _ask_with_rag(self, question, vector_store, memory):
        # Usa ConversationalRetrievalChain
        # Busca documentos relevantes
        # Genera respuesta con contexto
    
    def _ask_without_documents(self, question, memory):
        # Usa SimpleConversationChain
        # Solo usa historial conversacional
        # Genera respuesta general
```

---

## 🔧 Tecnologías Utilizadas

### 1. LangChain

**¿Qué es?**
- Framework de Python para construir aplicaciones con LLMs
- Proporciona abstracciones para chains, memory, prompts, etc.

**Componentes usados:**
- `ConversationalRetrievalChain`: Cadena que combina RAG con memoria
- `ConversationBufferMemory`: Almacena historial de conversación
- `PGVector`: Vector store basado en PostgreSQL
- `RecursiveCharacterTextSplitter`: Divide documentos en chunks
- `PyPDFLoader`: Carga documentos PDF

**Ventajas:**
- ✅ Abstracciones de alto nivel
- ✅ Integración fácil con múltiples LLMs
- ✅ Manejo automático de memoria
- ✅ Ecosistema grande y activo

**Desventajas:**
- ❌ Puede ser lento (muchas capas de abstracción)
- ❌ Cambios frecuentes en la API
- ❌ Curva de aprendizaje

---

### 2. OpenAI

**Modelos usados:**
- **LLM:** `gpt-4o-mini` (ChatOpenAI)
  - Propósito: Generar respuestas
  - Ventajas: Rápido, económico, buena calidad
  - Alternativas: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`

- **Embeddings:** `text-embedding-3-small`
  - Propósito: Convertir texto a vectores
  - Dimensiones: 1536
  - Alternativas: `text-embedding-3-large` (3072 dimensiones, más preciso)

**API de OpenAI:**
```python
# Chat Completions API
POST https://api.openai.com/v1/chat/completions
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "Eres un veterinario..."},
    {"role": "user", "content": "Pregunta"}
  ],
  "temperature": 0.3
}

# Embeddings API
POST https://api.openai.com/v1/embeddings
{
  "model": "text-embedding-3-small",
  "input": "Texto a convertir"
}
```

---

### 3. PostgreSQL + pgvector

**pgvector:**
- Extensión de PostgreSQL para almacenar vectores
- Permite búsqueda por similitud (cosine distance, L2 distance)

**Estructura de datos:**
```sql
CREATE TABLE langchain_pg_embedding (
    uuid UUID PRIMARY KEY,
    collection_id UUID,
    embedding vector(1536),  -- Vector de 1536 dimensiones
    document JSONB,           -- Contenido del chunk
    cmetadata JSONB          -- Metadata adicional
);

-- Índice para búsqueda rápida
CREATE INDEX ON langchain_pg_embedding 
USING ivfflat (embedding vector_cosine_ops);
```

**Búsqueda:**
```sql
-- Encuentra chunks más similares
SELECT document, embedding <-> '[vector de pregunta]' as distance
FROM langchain_pg_embedding
WHERE collection_id = 'pet_123_documents'
ORDER BY distance
LIMIT 4;
```

---

### 4. AWS S3

**Propósito:**
- Almacenar documentos PDF de mascotas
- URLs públicas para descargar PDFs

**Flujo:**
```
1. Usuario sube PDF → FastAPI
2. FastAPI → S3Service.upload_document()
3. S3Service → AWS S3 (put_object)
4. Retorna URL pública
5. URL se guarda en PostgreSQL (pet_photos.url)
6. LangChain descarga desde URL cuando se necesita
```

---

## 🔄 Alternativas Tecnológicas

### 1. Alternativas a LangChain

#### Opción A: LlamaIndex

**¿Qué es?**
- Framework especializado en RAG y aplicaciones de datos
- Más enfocado en indexación y recuperación

**Ventajas:**
- ✅ Mejor rendimiento en RAG
- ✅ Más opciones de índices (vector, keyword, hybrid)
- ✅ Mejor manejo de documentos grandes
- ✅ Integración con más bases de datos vectoriales

**Desventajas:**
- ❌ Menos opciones para memoria conversacional
- ❌ Ecosistema más pequeño

**Ejemplo de implementación:**
```python
from llama_index import VectorStoreIndex, Document
from llama_index.vector_stores import PGVectorStore
from llama_index.llms import OpenAI

# Crear índice
vector_store = PGVectorStore(...)
index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)

# Hacer pregunta
query_engine = index.as_query_engine()
response = query_engine.query("¿Cuándo fue la última vacunación?")
```

---

#### Opción B: Directo con OpenAI + SQL

**Enfoque:**
- Usar OpenAI API directamente sin frameworks
- Implementar RAG manualmente
- Usar SQL para búsqueda de documentos

**Ventajas:**
- ✅ Control total sobre el flujo
- ✅ Menos dependencias
- ✅ Más rápido (menos capas)
- ✅ Más fácil de debuggear

**Desventajas:**
- ❌ Más código para escribir
- ❌ Tienes que implementar todo manualmente
- ❌ Sin abstracciones útiles

**Ejemplo de implementación:**
```python
import openai
from pgvector.psycopg import register_vector
import psycopg

# 1. Generar embedding de la pregunta
response = openai.embeddings.create(
    model="text-embedding-3-small",
    input=question
)
question_embedding = response.data[0].embedding

# 2. Buscar documentos similares en PostgreSQL
conn = psycopg.connect(DATABASE_URL)
register_vector(conn)

with conn.cursor() as cur:
    cur.execute("""
        SELECT document, embedding <-> %s::vector as distance
        FROM langchain_pg_embedding
        WHERE collection_id = %s
        ORDER BY distance
        LIMIT 4
    """, (question_embedding, collection_id))
    
    results = cur.fetchall()

# 3. Construir prompt con documentos
context = "\n".join([r[0] for r in results])
prompt = f"Documentos:\n{context}\n\nPregunta: {question}"

# 4. Llamar a OpenAI
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Eres un veterinario..."},
        {"role": "user", "content": prompt}
    ]
)

answer = response.choices[0].message.content
```

---

#### Opción C: Haystack (by deepset)

**¿Qué es?**
- Framework de NLP para búsqueda y QA
- Muy bueno para RAG y pipelines complejos

**Ventajas:**
- ✅ Excelente para RAG
- ✅ Muchos componentes pre-construidos
- ✅ Buen rendimiento
- ✅ Soporte para múltiples bases de datos vectoriales

**Desventajas:**
- ❌ Curva de aprendizaje más pronunciada
- ❌ Menos popular que LangChain

**Ejemplo:**
```python
from haystack import Pipeline
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator

# Crear pipeline
pipeline = Pipeline()
pipeline.add_component("embedder", OpenAIDocumentEmbedder(...))
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(...))
pipeline.add_component("generator", OpenAIGenerator(...))

# Conectar componentes
pipeline.connect("embedder", "retriever")
pipeline.connect("retriever", "generator")

# Ejecutar
result = pipeline.run({"embedder": {"documents": documents}})
```

---

### 2. Alternativas a OpenAI

#### Opción A: Anthropic Claude (Claude API)

**Ventajas:**
- ✅ Mejor contexto (hasta 200K tokens)
- ✅ Muy bueno para análisis de documentos largos
- ✅ Respuestas más estructuradas

**Desventajas:**
- ❌ Más caro
- ❌ API diferente (requiere cambios en código)

**Ejemplo:**
```python
from anthropic import Anthropic

client = Anthropic(api_key="...")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": question}
    ]
)
```

---

#### Opción B: Google Gemini

**Ventajas:**
- ✅ Gratis hasta cierto límite
- ✅ Buen rendimiento
- ✅ Integración con Google Cloud

**Desventajas:**
- ❌ Menos maduro que OpenAI
- ❌ API puede cambiar

**Ejemplo:**
```python
import google.generativeai as genai

genai.configure(api_key="...")
model = genai.GenerativeModel('gemini-pro')

response = model.generate_content(question)
```

---

#### Opción C: Modelos Locales (Ollama, LlamaIndex)

**Ventajas:**
- ✅ 100% privado (datos no salen del servidor)
- ✅ Sin costos por API
- ✅ Control total

**Desventajas:**
- ❌ Requiere hardware potente (GPU)
- ❌ Menor calidad que modelos cloud
- ❌ Más complejo de configurar

**Ejemplo con Ollama:**
```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama2")

response = llm.invoke(question)
```

---

### 3. Alternativas a pgvector

#### Opción A: Pinecone

**Ventajas:**
- ✅ Servicio gestionado (no necesitas configurar)
- ✅ Muy rápido
- ✅ Escalable automáticamente

**Desventajas:**
- ❌ Costo adicional
- ❌ Dependencia externa
- ❌ Datos fuera de tu control

**Ejemplo:**
```python
from pinecone import Pinecone

pc = Pinecone(api_key="...")
index = pc.Index("pet-documents")

# Insertar
index.upsert(vectors=[...])

# Buscar
results = index.query(
    vector=question_embedding,
    top_k=4
)
```

---

#### Opción B: Weaviate

**Ventajas:**
- ✅ Open source
- ✅ Muy rápido
- ✅ Buenas características de búsqueda

**Desventajas:**
- ❌ Requiere servidor separado
- ❌ Más complejo de configurar

**Ejemplo:**
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Buscar
result = client.query.get("PetDocument", ["content"])\
    .with_near_vector({"vector": question_embedding})\
    .with_limit(4)\
    .do()
```

---

#### Opción C: Chroma

**Ventajas:**
- ✅ Muy fácil de usar
- ✅ Puede ser embebido o servidor
- ✅ Buen para desarrollo

**Desventajas:**
- ❌ Menos robusto para producción
- ❌ Menos características avanzadas

**Ejemplo:**
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("pet_documents")

# Insertar
collection.add(
    documents=["chunk 1", "chunk 2"],
    embeddings=[...],
    ids=["id1", "id2"]
)

# Buscar
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=4
)
```

---

#### Opción D: Qdrant

**Ventajas:**
- ✅ Open source
- ✅ Muy rápido
- ✅ Buen rendimiento

**Desventajas:**
- ❌ Requiere servidor separado
- ❌ Menos conocido

---

### 4. Alternativas para Memoria Conversacional

#### Opción A: Redis (Recomendado para Producción)

**Ventajas:**
- ✅ Muy rápido
- ✅ Persistente
- ✅ Escalable
- ✅ TTL automático

**Desventajas:**
- ❌ Requiere servidor Redis
- ❌ Dependencia adicional

**Ejemplo:**
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# Guardar mensaje
messages = [{"role": "user", "content": "..."}]
r.setex(
    f"chat:{session_id}",
    3600,  # TTL: 1 hora
    json.dumps(messages)
)

# Obtener mensajes
messages = json.loads(r.get(f"chat:{session_id}"))
```

---

#### Opción B: PostgreSQL (Tabla de Conversaciones)

**Ventajas:**
- ✅ Ya tienes PostgreSQL
- ✅ Persistente
- ✅ Puedes hacer queries complejas

**Desventajas:**
- ❌ Más lento que Redis
- ❌ Más complejo de implementar

**Ejemplo:**
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255),
    role VARCHAR(20),  -- 'user' o 'assistant'
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Obtener historial
SELECT role, content
FROM chat_messages
WHERE session_id = 'user123_pet456'
ORDER BY created_at;
```

---

#### Opción C: MongoDB

**Ventajas:**
- ✅ Flexible (documentos JSON)
- ✅ Bueno para datos no estructurados
- ✅ Escalable

**Desventajas:**
- ❌ Requiere servidor MongoDB
- ❌ Más complejo que Redis

**Ejemplo:**
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['pet_healthcare']
messages = db['chat_messages']

# Guardar mensaje
messages.insert_one({
    "session_id": "user123_pet456",
    "role": "user",
    "content": "Pregunta",
    "timestamp": datetime.now()
})

# Obtener historial
history = list(messages.find(
    {"session_id": "user123_pet456"}
).sort("timestamp", 1))
```

---

## 🎯 Enfoques de Implementación

### Enfoque 1: RAG con Memoria (Actual)

**Arquitectura:**
```
Pregunta → Buscar documentos → Construir prompt con historial + documentos → LLM → Respuesta
```

**Ventajas:**
- ✅ Respuestas basadas en documentos reales
- ✅ Memoria conversacional
- ✅ Preciso para información específica

**Desventajas:**
- ❌ Más lento (búsqueda + generación)
- ❌ Más costoso (embeddings + LLM)
- ❌ Requiere documentos con texto

**Cuándo usar:**
- Cuando tienes documentos PDF con información específica
- Cuando necesitas respuestas precisas basadas en datos reales
- Cuando la información cambia frecuentemente

---

### Enfoque 2: Solo Memoria Conversacional (Sin RAG)

**Arquitectura:**
```
Pregunta → Construir prompt con historial → LLM → Respuesta
```

**Ventajas:**
- ✅ Más rápido
- ✅ Más barato
- ✅ Funciona sin documentos

**Desventajas:**
- ❌ No puede acceder a documentos específicos
- ❌ Respuestas basadas solo en conocimiento general del LLM

**Cuándo usar:**
- Para preguntas generales sobre veterinaria
- Cuando no hay documentos disponibles
- Para consultas rápidas

---

### Enfoque 3: RAG sin Memoria

**Arquitectura:**
```
Pregunta → Buscar documentos → Construir prompt con documentos → LLM → Respuesta
```

**Ventajas:**
- ✅ Respuestas basadas en documentos
- ✅ Más rápido que con memoria
- ✅ Menos tokens (no incluye historial)

**Desventajas:**
- ❌ No recuerda conversaciones anteriores
- ❌ Cada pregunta es independiente

**Cuándo usar:**
- Cuando cada pregunta es independiente
- Cuando no necesitas contexto conversacional
- Para análisis de documentos únicos

---

### Enfoque 4: Memoria con Resumen (Summary Memory)

**Arquitectura:**
```
Pregunta → Resumir historial antiguo → Construir prompt con resumen + pregunta → LLM → Respuesta
```

**Ventajas:**
- ✅ Mantiene contexto sin límite de tokens
- ✅ Más eficiente que buffer completo

**Desventajas:**
- ❌ Puede perder detalles específicos
- ❌ Más complejo de implementar

**Ejemplo con LangChain:**
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=llm,  # Necesita LLM para resumir
    return_messages=True
)

# El historial se resume automáticamente cuando crece
```

---

### Enfoque 5: Memoria con Ventana Deslizante

**Arquitectura:**
```
Pregunta → Mantener solo últimos N mensajes → Construir prompt → LLM → Respuesta
```

**Ventajas:**
- ✅ Control preciso sobre tokens
- ✅ Mantiene contexto reciente
- ✅ Simple de implementar

**Desventajas:**
- ❌ Pierde contexto antiguo
- ❌ Puede perder información importante

**Implementación actual:**
```python
# Ya implementado en ChatController._limit_memory_messages()
# Mantiene solo los últimos 12 mensajes (6 interacciones)
```

---

### Enfoque 6: Memoria con Base de Conocimiento Externa

**Arquitectura:**
```
Pregunta → Buscar en KB → Construir prompt con KB + historial → LLM → Respuesta
```

**Ventajas:**
- ✅ Puede acceder a información estructurada
- ✅ Más preciso que solo documentos PDF
- ✅ Puede combinar múltiples fuentes

**Desventajas:**
- ❌ Más complejo
- ❌ Requiere mantener base de conocimiento

**Ejemplo:**
```python
# Buscar en base de conocimiento estructurada
kb_results = knowledge_base.search(question)

# Combinar con documentos PDF
all_context = kb_results + pdf_documents

# Generar respuesta
response = llm.invoke(prompt_with_context)
```

---

## 💾 Memoria Conversacional

### Tipos de Memoria en LangChain

#### 1. ConversationBufferMemory (Actual)

**Cómo funciona:**
- Almacena todos los mensajes en orden
- No tiene límite por defecto
- Simple y directo

**Implementación:**
```python
memory = ConversationBufferMemory(
    return_messages=True,  # Retorna lista de mensajes
    memory_key="chat_history",
    output_key="answer"
)

# Guardar
memory.save_context(
    {"input": "Pregunta"},
    {"output": "Respuesta"}
)

# Obtener
memory_vars = memory.load_memory_variables({})
history = memory_vars["chat_history"]  # Lista de mensajes
```

**Estructura interna:**
```python
memory.chat_memory.messages = [
    HumanMessage(content="Pregunta 1"),
    AIMessage(content="Respuesta 1"),
    HumanMessage(content="Pregunta 2"),
    AIMessage(content="Respuesta 2"),
    ...
]
```

---

#### 2. ConversationSummaryMemory

**Cómo funciona:**
- Resume el historial antiguo cuando crece
- Mantiene mensajes recientes completos
- Usa LLM para generar resumen

**Ventajas:**
- ✅ Mantiene contexto sin límite de tokens
- ✅ Eficiente para conversaciones largas

**Desventajas:**
- ❌ Puede perder detalles en el resumen
- ❌ Requiere llamadas adicionales al LLM

**Ejemplo:**
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=llm,  # Necesita LLM para resumir
    return_messages=True
)

# Cuando el historial crece:
# - Mensajes antiguos → Se resumen
# - Mensajes recientes → Se mantienen completos
```

---

#### 3. ConversationBufferWindowMemory

**Cómo funciona:**
- Mantiene solo los últimos N mensajes
- Similar a lo que ya implementamos manualmente

**Ejemplo:**
```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=6,  # Mantiene últimos 6 mensajes
    return_messages=True
)
```

---

#### 4. ConversationSummaryBufferMemory

**Cómo funciona:**
- Combina buffer y summary
- Mantiene últimos N mensajes completos
- Resume el resto

**Ejemplo:**
```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=2000,  # Límite de tokens
    return_messages=True
)
```

---

### Implementación de Memoria en el Sistema Actual

**Almacenamiento:**
```python
# En memoria (no persistente)
_conversation_memories: Dict[str, ConversationBufferMemory] = {}

# Estructura:
# {
#   "user123_pet456": ConversationBufferMemory(...),
#   "user789_pet101": ConversationBufferMemory(...),
#   ...
# }
```

**Limitación Manual:**
```python
def _limit_memory_messages(memory):
    # Obtiene todos los mensajes
    messages = memory.load_memory_variables({})["chat_history"]
    
    # Si excede 12 mensajes (6 interacciones)
    if len(messages) > 12:
        # Mantiene solo los últimos 12
        messages_to_keep = messages[-12:]
        
        # Limpia y restaura
        memory.chat_memory.clear()
        for msg in messages_to_keep:
            memory.chat_memory.add_message(msg)
```

**¿Por qué limitar a 6 interacciones?**
- Control de costos (menos tokens = menos costo)
- Evitar que el contexto sea demasiado largo
- Mejor rendimiento (menos procesamiento)

---

## 🔍 RAG (Retrieval Augmented Generation)

### ¿Qué es RAG?

**RAG** es una técnica que combina:
1. **Retrieval (Recuperación)**: Buscar información relevante en documentos
2. **Augmented (Aumentado)**: Aumentar el prompt con esa información
3. **Generation (Generación)**: Generar respuesta usando el contexto

### Flujo de RAG

```
1. Usuario pregunta: "¿Cuándo fue la última vacunación?"
                    ↓
2. Generar embedding de la pregunta
   [0.123, -0.456, ..., 0.789]  (1536 dimensiones)
                    ↓
3. Buscar en vector store (búsqueda por similitud)
   - Comparar embedding de pregunta con embeddings de chunks
   - Encontrar top 4 chunks más similares
                    ↓
4. Recuperar chunks relevantes
   - "Vacunación aplicada el 17/01/2019..."
   - "Próxima dosis: 18/01/2019..."
                    ↓
5. Construir prompt aumentado
   System: "Eres un veterinario experto..."
   Context: "Documentos relevantes: [chunks recuperados]"
   History: "[conversación anterior]"
   Question: "¿Cuándo fue la última vacunación?"
                    ↓
6. Enviar a LLM
                    ↓
7. LLM genera respuesta usando el contexto
   "Según los documentos, la última vacunación fue el 17/01/2019..."
                    ↓
8. Retornar respuesta + documentos fuente
```

### Componentes de RAG

#### 1. Document Loader

**Propósito:** Cargar documentos desde diferentes fuentes

**Opciones:**
- `PyPDFLoader`: PDFs locales o URLs
- `UnstructuredFileLoader`: Múltiples formatos
- `CSVLoader`: Archivos CSV
- `TextLoader`: Archivos de texto plano

**Ejemplo:**
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("documento.pdf")
documents = loader.load()  # Lista de Document (una por página)
```

---

#### 2. Text Splitter

**Propósito:** Dividir documentos largos en chunks más pequeños

**Tipos:**
- `RecursiveCharacterTextSplitter`: Divide por caracteres (actual)
- `TokenTextSplitter`: Divide por tokens
- `CharacterTextSplitter`: Divide por caracteres (simple)
- `MarkdownHeaderTextSplitter`: Divide markdown por headers

**Parámetros importantes:**
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Tamaño máximo del chunk
    chunk_overlap=200,    # Overlap entre chunks
    length_function=len   # Función para medir longitud
)
```

**¿Por qué overlap?**
- Evita perder información en los bordes
- Mejora la recuperación de información que cruza chunks

---

#### 3. Embeddings

**Propósito:** Convertir texto a vectores numéricos

**Modelos disponibles:**
- `OpenAIEmbeddings`: text-embedding-3-small, text-embedding-3-large
- `HuggingFaceEmbeddings`: Modelos open source
- `CohereEmbeddings`: API de Cohere
- `SentenceTransformers`: Modelos locales

**Ejemplo:**
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Generar embedding
vector = embeddings.embed_query("Vacunación aplicada el 17/01/2019")
# Resultado: [0.123, -0.456, ..., 0.789]  (1536 números)
```

**Dimensiones:**
- `text-embedding-3-small`: 1536 dimensiones
- `text-embedding-3-large`: 3072 dimensiones (más preciso, más caro)

---

#### 4. Vector Store

**Propósito:** Almacenar y buscar vectores eficientemente

**Opciones:**
- `PGVector`: PostgreSQL + pgvector (actual)
- `Pinecone`: Servicio gestionado
- `Weaviate`: Open source
- `Chroma`: Embeddable
- `FAISS`: Local, muy rápido
- `Qdrant`: Open source, rápido

**Búsqueda por similitud:**
```python
# Búsqueda por distancia coseno (similaridad)
results = vector_store.similarity_search(
    query="vacunación",
    k=4  # Top 4 resultados
)

# Búsqueda con score (distancia)
results = vector_store.similarity_search_with_score(
    query="vacunación",
    k=4
)
# Retorna: [(Document, score), ...]
```

---

#### 5. Retriever

**Propósito:** Interfaz para recuperar documentos relevantes

**Tipos:**
- `VectorStoreRetriever`: Búsqueda por similitud (actual)
- `BM25Retriever`: Búsqueda por palabras clave
- `EnsembleRetriever`: Combina múltiples métodos
- `ContextualCompressionRetriever`: Comprime contexto

**Ejemplo:**
```python
retriever = vector_store.as_retriever(
    search_kwargs={"k": 4}  # Top 4 documentos
)

# Buscar
docs = retriever.get_relevant_documents("vacunación")
```

---

#### 6. Chain

**Propósito:** Orquestar todo el flujo RAG

**Tipos:**
- `ConversationalRetrievalChain`: RAG + memoria (actual)
- `RetrievalQA`: RAG simple sin memoria
- `RetrievalQAWithSourcesChain`: RAG con fuentes

**Flujo interno:**
```python
chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)

# Internamente hace:
# 1. Obtiene historial de memoria
# 2. Busca documentos relevantes
# 3. Construye prompt con historial + documentos + pregunta
# 4. Invoca LLM
# 5. Guarda en memoria
# 6. Retorna respuesta + documentos fuente
```

---

### Optimizaciones de RAG

#### 1. Chunking Inteligente

**Problema:** Dividir por caracteres puede cortar información importante

**Solución:** Dividir por estructura semántica

```python
from langchain.text_splitters import MarkdownHeaderTextSplitter

# Dividir markdown por headers
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header 1")])
chunks = splitter.split_text(markdown_text)
```

---

#### 2. Re-ranking

**Problema:** Los primeros resultados pueden no ser los más relevantes

**Solución:** Re-ordenar resultados con modelo de re-ranking

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Comprimir y re-ordenar
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)
```

---

#### 3. Hybrid Search

**Problema:** Búsqueda solo por similitud puede perder información

**Solución:** Combinar búsqueda semántica + búsqueda por palabras clave

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# Búsqueda híbrida
bm25_retriever = BM25Retriever.from_documents(documents)
vector_retriever = vector_store.as_retriever()

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]  # 50% cada uno
)
```

---

#### 4. Metadata Filtering

**Problema:** Buscar en todos los documentos puede ser ineficiente

**Solución:** Filtrar por metadata antes de buscar

```python
# Filtrar por metadata
retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 4,
        "filter": {"pet_id": "876835fa-6c7d-4c97-bc18-4e5728e8bc13"}
    }
)
```

---

## ⚡ Optimizaciones y Mejores Prácticas

### 1. Optimización de Costos

#### Reducir Tokens

```python
# ❌ Mal: Incluir todo el historial
prompt = f"{full_history}\n{question}"

# ✅ Bien: Limitar historial
recent_history = history[-6:]  # Solo últimos 6 mensajes
prompt = f"{recent_history}\n{question}"

# ✅ Mejor: Resumir historial antiguo
summary = summarize_old_history(history[:-6])
prompt = f"{summary}\n{recent_history}\n{question}"
```

#### Usar Modelos Más Baratos

```python
# Para embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # Más barato

# Para generación
llm = ChatOpenAI(model="gpt-4o-mini")  # Más barato que gpt-4o
```

#### Cachear Embeddings

```python
# No regenerar embeddings de documentos que no han cambiado
# Guardar embeddings en base de datos con hash del documento
```

---

### 2. Optimización de Rendimiento

#### Pre-cargar Vector Store

```python
# En lugar de crear vector store en cada pregunta
# Crear una vez y reutilizar
vector_store_cache = {}

def get_vector_store(pet_id):
    if pet_id not in vector_store_cache:
        vector_store_cache[pet_id] = create_vector_store(pet_id)
    return vector_store_cache[pet_id]
```

#### Usar Streaming

```python
# Respuestas en tiempo real (token por token)
for chunk in chain.stream({"question": question}):
    print(chunk, end="", flush=True)
```

#### Paralelizar Búsquedas

```python
# Buscar en múltiples colecciones en paralelo
import asyncio

async def search_multiple_sources(question):
    results = await asyncio.gather(
        search_vaccinations(question),
        search_visits(question),
        search_lab_results(question)
    )
    return combine_results(results)
```

---

### 3. Mejora de Calidad

#### Mejorar Prompts

```python
# ❌ Mal: Prompt genérico
prompt = "Responde la pregunta: {question}"

# ✅ Bien: Prompt específico con instrucciones claras
prompt = """Eres un veterinario experto. 
Responde SOLO basándote en los documentos proporcionados.
Si la información no está en los documentos, di claramente que no la encontraste.
Sé específico y menciona fechas cuando estén disponibles.

Documentos: {context}
Pregunta: {question}
Respuesta:"""
```

#### Validar Respuestas

```python
# Validar que la respuesta es relevante
def validate_answer(answer, question, documents):
    # Verificar que menciona información de los documentos
    # Verificar que responde la pregunta
    # Verificar que no alucina información
    pass
```

#### Usar Few-Shot Examples

```python
prompt = """Eres un veterinario experto.

Ejemplos:
Usuario: "¿Cuándo fue la última vacunación?"
Veterinario: "Según los documentos, la última vacunación fue el 17/01/2019 con la vacuna Vanguard Plus 5 L4."

Usuario: {question}
Veterinario:"""
```

---

### 4. Manejo de Errores

#### Timeouts

```python
import asyncio

try:
    response = await asyncio.wait_for(
        llm.ainvoke(messages),
        timeout=30.0  # 30 segundos máximo
    )
except asyncio.TimeoutError:
    return {"error": "Timeout al generar respuesta"}
```

#### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def ask_question_with_retry(question):
    return llm.invoke(question)
```

#### Fallbacks

```python
try:
    # Intentar con documentos
    answer = ask_with_rag(question, documents)
except Exception:
    # Fallback a conversación general
    answer = ask_without_documents(question)
```

---

## 📊 Comparación de Enfoques

### Tabla Comparativa

| Enfoque | Velocidad | Costo | Precisión | Complejidad | Memoria |
|---------|----------|------|-----------|-------------|---------|
| RAG + Memoria (Actual) | Media | Alto | Alta | Alta | ✅ |
| Solo Memoria | Alta | Media | Media | Baja | ✅ |
| RAG sin Memoria | Media | Alto | Alta | Media | ❌ |
| Memoria con Resumen | Media | Media | Media | Alta | ✅ |
| Directo OpenAI | Alta | Bajo | Baja | Baja | ❌ |

---

## 🎓 Conceptos Clave para Entender

### 1. Embeddings

**¿Qué son?**
- Representación numérica del significado del texto
- Textos similares tienen vectores similares
- Permite búsqueda semántica (no solo palabras clave)

**Ejemplo:**
```
"Vacunación de perro" → [0.1, -0.3, 0.5, ...]
"Vacuna canina"      → [0.12, -0.28, 0.52, ...]  (similar)
"Comida de gato"     → [-0.2, 0.4, -0.1, ...]   (diferente)
```

**Distancia:**
- **Coseno**: Mide el ángulo entre vectores (0-1, donde 1 = idéntico)
- **Euclidiana**: Mide distancia directa
- **Punto**: Producto punto (más rápido)

---

### 2. Vector Store

**¿Qué es?**
- Base de datos especializada en almacenar y buscar vectores
- Permite búsqueda por similitud muy rápida

**Índices:**
- **IVFFlat**: Índice invertido (rápido, aproximado)
- **HNSW**: Hierarchical Navigable Small World (muy rápido)
- **Exact**: Búsqueda exacta (lento, preciso)

---

### 3. Chunking

**¿Por qué dividir?**
- LLMs tienen límite de tokens (ej: 128K para GPT-4)
- Búsqueda más precisa (chunks pequeños = más específicos)
- Mejor rendimiento (menos tokens a procesar)

**Estrategias:**
- **Por tamaño**: Dividir en chunks de N caracteres
- **Por estructura**: Dividir por párrafos, headers, etc.
- **Por semántica**: Dividir por significado (más complejo)

---

### 4. Retrieval

**Métodos:**
- **Dense Retrieval**: Búsqueda por embeddings (semántica)
- **Sparse Retrieval**: Búsqueda por palabras clave (BM25, TF-IDF)
- **Hybrid**: Combinación de ambos

**Re-ranking:**
- Re-ordenar resultados con modelo más sofisticado
- Mejora precisión pero aumenta costo

---

### 5. Generation

**Parámetros importantes:**
- **Temperature**: Creatividad (0.0 = determinista, 1.0 = creativo)
- **Max Tokens**: Longitud máxima de respuesta
- **Top P**: Nucleus sampling (controla diversidad)
- **Frequency Penalty**: Penaliza repeticiones

---

## 🔬 Ejemplo de Implementación Completa

### Versión Simplificada (Sin Frameworks)

```python
import openai
import psycopg
from pgvector.psycopg import register_vector
import json

class SimpleVetChat:
    def __init__(self, api_key, db_url):
        self.api_key = api_key
        self.db_url = db_url
        self.memories = {}  # {session_id: [mensajes]}
    
    def ask_question(self, question, session_id, pet_id=None):
        # 1. Obtener historial
        history = self.memories.get(session_id, [])
        
        # 2. Buscar documentos si hay pet_id
        context = ""
        if pet_id:
            context = self._search_documents(question, pet_id)
        
        # 3. Construir mensajes
        messages = [
            {"role": "system", "content": "Eres un veterinario experto..."}
        ]
        
        # Agregar historial
        for msg in history[-6:]:  # Últimos 6 mensajes
            messages.append(msg)
        
        # Agregar contexto si hay documentos
        if context:
            messages.append({
                "role": "system",
                "content": f"Documentos relevantes:\n{context}"
            })
        
        # Agregar pregunta actual
        messages.append({"role": "user", "content": question})
        
        # 4. Llamar a OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        # 5. Guardar en memoria
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        
        # Limitar a 12 mensajes (6 interacciones)
        if len(history) > 12:
            history = history[-12:]
        
        self.memories[session_id] = history
        
        return {
            "answer": answer,
            "chat_history": history
        }
    
    def _search_documents(self, question, pet_id):
        # 1. Generar embedding de pregunta
        embedding_response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=question
        )
        question_embedding = embedding_response.data[0].embedding
        
        # 2. Buscar en PostgreSQL
        conn = psycopg.connect(self.db_url)
        register_vector(conn)
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT document->>'page_content' as content
                FROM langchain_pg_embedding
                WHERE collection_id = (
                    SELECT uuid FROM langchain_pg_collection 
                    WHERE name = %s
                )
                ORDER BY embedding <-> %s::vector
                LIMIT 4
            """, (f"pet_{pet_id}_documents", question_embedding))
            
            results = cur.fetchall()
        
        # 3. Combinar resultados
        context = "\n\n".join([r[0] for r in results])
        return context
```

---

## 🚀 Mejoras Futuras

### 1. Persistencia de Memoria

**Actual:** Memoria en RAM (se pierde al reiniciar)

**Mejora:** Usar Redis o PostgreSQL

```python
# Con Redis
import redis
import json

r = redis.Redis(...)

def save_memory(session_id, messages):
    r.setex(
        f"chat:{session_id}",
        3600,  # TTL: 1 hora
        json.dumps(messages)
    )

def load_memory(session_id):
    data = r.get(f"chat:{session_id}")
    return json.loads(data) if data else []
```

---

### 2. Streaming de Respuestas

**Actual:** Respuesta completa al final

**Mejora:** Respuesta token por token

```python
from fastapi.responses import StreamingResponse

@router.post("/chat/pets/{pet_id}/ask-stream")
async def ask_streaming(pet_id: str, request: ChatQuestionRequest):
    async def generate():
        async for chunk in chain.astream({"question": request.question}):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

### 3. Caché de Respuestas

**Mejora:** Cachear respuestas a preguntas comunes

```python
import hashlib
import redis

def get_cached_answer(question):
    question_hash = hashlib.md5(question.encode()).hexdigest()
    cached = r.get(f"answer:{question_hash}")
    return json.loads(cached) if cached else None

def cache_answer(question, answer):
    question_hash = hashlib.md5(question.encode()).hexdigest()
    r.setex(f"answer:{question_hash}", 3600, json.dumps(answer))
```

---

### 4. Análisis de Sentimiento

**Mejora:** Detectar urgencia en preguntas

```python
from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_urgency(question):
    result = sentiment_analyzer(question)
    if "urgente" in question.lower() or result[0]["label"] == "NEGATIVE":
        return "high"
    return "normal"
```

---

## 📚 Recursos Adicionales

### Documentación Oficial
- **LangChain**: https://python.langchain.com/
- **OpenAI API**: https://platform.openai.com/docs
- **pgvector**: https://github.com/pgvector/pgvector
- **FastAPI**: https://fastapi.tiangolo.com/

### Tutoriales Recomendados
- **RAG Tutorial**: https://python.langchain.com/docs/use_cases/question_answering/
- **Memory Tutorial**: https://python.langchain.com/docs/modules/memory/
- **Vector Stores**: https://python.langchain.com/docs/integrations/vectorstores/

### Herramientas Útiles
- **LangSmith**: Monitoreo y debugging de aplicaciones LangChain
- **Weights & Biases**: Tracking de experimentos
- **Postman**: Probar endpoints de la API

---

## 🎯 Resumen Ejecutivo

### Arquitectura Actual

1. **Cliente** → FastAPI → **Controlador** → **Servicio LangChain**
2. **Servicio** carga PDFs, genera embeddings, almacena en PGVector
3. **Pregunta** → Busca documentos relevantes → Construye prompt → LLM → Respuesta
4. **Memoria** se mantiene en RAM (limitada a 6 interacciones)

### Tecnologías Clave

- **LangChain**: Framework para orquestar LLMs
- **OpenAI**: GPT-4o-mini para generación, text-embedding-3-small para embeddings
- **pgvector**: Almacenamiento de vectores en PostgreSQL
- **ConversationBufferMemory**: Memoria conversacional

### Alternativas Principales

- **LlamaIndex**: Mejor para RAG puro
- **Directo OpenAI**: Más control, menos abstracción
- **Redis**: Mejor para memoria en producción
- **Pinecone/Weaviate**: Vector stores gestionados

---

**Última actualización:** Enero 2025  
**Versión:** 1.0


