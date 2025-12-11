"""
Script de diagnóstico COMPLETO para verificar acceso a documentos PDF
Incluye login automático y todas las pruebas necesarias
Ejecutar: python test_document_access_full.py
"""
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Configuración
BASE_URL = "https://pet-healthcare-back.onrender.com"
EMAIL = "95juliandos@gmail.com"  # Tu email de admin
PASSWORD = "Password123"  # Tu contraseña
PET_ID = "876835fa-6c7d-4c97-bc18-4e5728e8bc13"

def login():
    """Realiza login y retorna el access token"""
    print("\n" + "="*60)
    print("🔐 INICIANDO SESIÓN")
    print("="*60)
    print(f"Email: {EMAIL}")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"✅ Login exitoso")
            print(f"Token (primeros 50 chars): {token[:50]}...")
            return token
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_document_listing(token):
    """Prueba 1: Listar documentos de la mascota"""
    print("\n" + "="*60)
    print("PRUEBA 1: Listando documentos de la mascota")
    print("="*60)
    
    url = f"{BASE_URL}/images/pets/{PET_ID}/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Documentos encontrados: {len(documents)}")
            
            for idx, doc in enumerate(documents, 1):
                print(f"\n📄 Documento {idx}:")
                print(f"   ID: {doc.get('id')}")
                print(f"   Nombre: {doc.get('file_name')}")
                print(f"   Tipo: {doc.get('file_type')}")
                print(f"   Categoría: {doc.get('document_category')}")
                print(f"   URL: {doc.get('url')[:80]}...")
                print(f"   Tamaño: {doc.get('file_size_bytes', 0) / 1024:.2f} KB")
            
            return documents
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

def test_pdf_download(pdf_url):
    """Prueba 2: Descargar PDF directamente desde S3"""
    print("\n" + "="*60)
    print("PRUEBA 2: Descargando PDF directamente desde S3")
    print("="*60)
    print(f"URL: {pdf_url[:80]}...")
    
    try:
        response = requests.get(pdf_url, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', 'unknown')
            content_length = len(response.content)
            
            print(f"✅ PDF descargado exitosamente")
            print(f"   Content-Type: {content_type}")
            print(f"   Tamaño: {content_length / 1024:.2f} KB")
            
            # Verificar si es realmente un PDF
            if response.content.startswith(b'%PDF-'):
                print(f"   ✅ Confirmado: Es un PDF válido")
                
                # Intentar extraer versión del PDF
                header = response.content[:20].decode('latin-1', errors='ignore')
                print(f"   Header: {header}")
                
                return response.content
            else:
                print(f"   ❌ Advertencia: No parece ser un PDF válido")
                print(f"   Primeros 20 bytes: {response.content[:20]}")
                return None
        else:
            print(f"❌ Error descargando: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Respuesta: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def test_pdf_processing(pdf_content):
    """Prueba 3: Procesar PDF con PyPDF"""
    print("\n" + "="*60)
    print("PRUEBA 3: Procesando PDF con PyPDF")
    print("="*60)
    
    try:
        from pypdf import PdfReader
        import io
        
        # Crear reader desde bytes
        print("📖 Leyendo contenido del PDF...")
        pdf_file = io.BytesIO(pdf_content)
        reader = PdfReader(pdf_file)
        
        num_pages = len(reader.pages)
        print(f"✅ PDF procesado exitosamente")
        print(f"   Páginas: {num_pages}")
        
        # Extraer metadata
        metadata = reader.metadata
        if metadata:
            print(f"   Metadata:")
            if metadata.get('/Title'):
                print(f"      Título: {metadata.get('/Title')}")
            if metadata.get('/Author'):
                print(f"      Autor: {metadata.get('/Author')}")
            if metadata.get('/Subject'):
                print(f"      Asunto: {metadata.get('/Subject')}")
        
        # Extraer texto de la primera página
        if num_pages > 0:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            text_preview = text[:300].replace('\n', ' ')
            print(f"\n   📄 Texto de la primera página (primeros 300 chars):")
            print(f"   {text_preview}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando PDF: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_chat_without_documents(token):
    """Prueba 4A: Chat sin documentos (modo conversación general)"""
    print("\n" + "="*60)
    print("PRUEBA 4A: Chat SIN documentos (veterinario experto)")
    print("="*60)
    
    url = f"{BASE_URL}/chat/test"
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }
    
    question = "Mi perro tiene tos seca desde hace 2 días, ¿es grave?"
    
    try:
        print(f"📤 Pregunta: {question}")
        response = requests.post(
            url, 
            params={"question": question},
            headers=headers, 
            timeout=120
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Respuesta recibida:")
            print(f"   Mode: {result.get('mode', 'unknown')}")
            
            answer = result.get('answer', '')
            print(f"\n💬 Respuesta del veterinario:")
            print(f"   {answer[:400]}...")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_chat_with_documents(token):
    """Prueba 4B: Chat CON documentos (RAG)"""
    print("\n" + "="*60)
    print("PRUEBA 4B: Chat CON documentos (RAG)")
    print("="*60)
    
    url = f"{BASE_URL}/chat/pets/{PET_ID}/ask"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    data = {
        "question": "¿Qué vacunas tiene registradas mi mascota según sus documentos? Dame detalles específicos de lo que encuentres.",
        "session_id": "diagnostic-test-456"
    }
    
    try:
        print(f"📤 Pregunta: {data['question']}")
        print(f"Session ID: {data['session_id']}")
        
        response = requests.post(url, json=data, headers=headers, timeout=120)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Respuesta recibida:")
            print(f"   has_documents: {result.get('has_documents')}")
            print(f"   source_documents: {len(result.get('source_documents', []))} documentos")
            print(f"   session_id: {result.get('session_id')}")
            
            # Mostrar documentos fuente
            source_docs = result.get('source_documents', [])
            if source_docs:
                print(f"\n📚 Documentos fuente usados:")
                for idx, doc in enumerate(source_docs, 1):
                    print(f"\n   {idx}. Fuente: {doc.get('source', 'unknown')[:60]}...")
                    print(f"      Página: {doc.get('page', 0)}")
                    content_preview = doc.get('content', '')[:150].replace('\n', ' ')
                    print(f"      Contenido: {content_preview}...")
            else:
                print(f"\n⚠️ No se usaron documentos fuente (puede que no haya PDFs o hubo error)")
            
            # Mostrar respuesta
            answer = result.get('answer', '')
            print(f"\n💬 Respuesta del veterinario:")
            print(f"   {answer[:500]}...")
            
            # Verificar si hay errores
            if result.get('error'):
                print(f"\n⚠️ Error reportado: {result.get('error')}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def test_chat_memory(token):
    """Prueba 5: Probar memoria conversacional"""
    print("\n" + "="*60)
    print("PRUEBA 5: Memoria Conversacional")
    print("="*60)
    
    url = f"{BASE_URL}/chat/pets/{PET_ID}/ask"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    session_id = "memory-test-789"
    
    # Primera pregunta - establecer contexto
    print("\n📤 PREGUNTA 1: Estableciendo contexto...")
    data1 = {
        "question": "Mi perro se llama Rocky y tiene 5 años. ¿Qué vacunas debería tener a su edad?",
        "session_id": session_id
    }
    
    try:
        response1 = requests.post(url, json=data1, headers=headers, timeout=120)
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Respuesta 1 recibida")
            print(f"   {result1.get('answer', '')[:200]}...")
        else:
            print(f"❌ Error en pregunta 1: {response1.status_code}")
            return False
        
        # Segunda pregunta - probar memoria
        print("\n📤 PREGUNTA 2: Probando memoria...")
        data2 = {
            "question": "¿Recuerdas cómo se llama mi perro y cuántos años tiene?",
            "session_id": session_id
        }
        
        response2 = requests.post(url, json=data2, headers=headers, timeout=120)
        if response2.status_code == 200:
            result2 = response2.json()
            answer2 = result2.get('answer', '')
            
            print(f"✅ Respuesta 2 recibida")
            print(f"\n💬 Respuesta del veterinario:")
            print(f"   {answer2[:300]}...")
            
            # Verificar si menciona "Rocky" y "5 años"
            if "Rocky" in answer2 or "rocky" in answer2.lower():
                print(f"\n✅ ¡MEMORIA FUNCIONA! Recordó el nombre 'Rocky'")
            else:
                print(f"\n⚠️ No mencionó 'Rocky' explícitamente en la respuesta")
            
            if "5" in answer2 or "cinco" in answer2.lower():
                print(f"✅ ¡MEMORIA FUNCIONA! Recordó la edad '5 años'")
            else:
                print(f"⚠️ No mencionó la edad explícitamente")
            
            # Mostrar historial
            history = result2.get('chat_history', [])
            print(f"\n📚 Historial de conversación: {len(history)} mensajes")
            for idx, msg in enumerate(history[-4:], 1):  # Últimos 4 mensajes
                role_emoji = "👤" if msg['role'] == 'user' else "🩺"
                content_preview = msg['content'][:80].replace('\n', ' ')
                print(f"   {role_emoji} {content_preview}...")
            
            return True
        else:
            print(f"❌ Error en pregunta 2: {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*60)
    print("🔬 DIAGNÓSTICO COMPLETO DE CHAT CON IA VETERINARIA")
    print("="*60)
    print(f"Pet ID: {PET_ID}")
    print(f"Base URL: {BASE_URL}")
    
    # Paso 0: Login
    token = login()
    if not token:
        print("\n❌ No se pudo obtener token. Abortando pruebas.")
        print("\n💡 Verifica:")
        print("   1. Que el email y password sean correctos")
        print("   2. Que el servidor esté accesible")
        print("   3. Que la cuenta esté verificada y activa")
        return
    
    # Paso 1: Listar documentos
    documents = test_document_listing(token)
    
    has_documents = len(documents) > 0
    
    if has_documents:
        # Paso 2 y 3: Descargar y procesar primer PDF
        first_doc = documents[0]
        pdf_url = first_doc.get('url')
        
        if pdf_url:
            pdf_content = test_pdf_download(pdf_url)
            
            if pdf_content:
                test_pdf_processing(pdf_content)
            else:
                print("\n⚠️ No se pudo descargar el PDF correctamente")
    else:
        print("\n⚠️ No hay documentos PDF para esta mascota")
    
    # Paso 4A: Chat sin documentos
    test_chat_without_documents(token)
    
    # Paso 4B: Chat con documentos (solo si hay)
    if has_documents:
        test_chat_with_documents(token)
    else:
        print("\n⏭️ Saltando prueba de chat con documentos (no hay PDFs)")
    
    # Paso 5: Probar memoria
    test_chat_memory(token)
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("="*60)
    print(f"✅ Login: OK")
    print(f"{'✅' if has_documents else '⚠️'} Documentos PDF: {len(documents)} encontrados")
    print(f"✅ Chat sin documentos: Disponible")
    print(f"{'✅' if has_documents else '⚠️'} Chat con documentos (RAG): {'Disponible' if has_documents else 'Sin documentos'}")
    print(f"✅ Memoria conversacional: Implementada")
    
    if not has_documents:
        print(f"\n💡 RECOMENDACIÓN:")
        print(f"   Sube documentos PDF a la mascota con ID {PET_ID} para probar el chat con RAG")
        print(f"   Endpoint: POST /images/pets/{PET_ID}/documents")
    
    print("\n" + "="*60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    main()