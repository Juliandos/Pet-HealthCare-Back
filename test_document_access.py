"""
Script de diagnóstico para verificar acceso a documentos PDF
Ejecutar: python test_document_access.py
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
PET_ID = "876835fa-6c7d-4c97-bc18-4e5728e8bc13"
BASE_URL = "https://pet-healthcare-back.onrender.com"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwY2RhNzRlNS02N2M0LTQyNjItOTEyYy03Njk1ZTAxZDhkY2YiLCJlbWFpbCI6Ijk1anVsaWFuZG9zQGdtYWlsLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NTQwOTg2OSwiaWF0IjoxNzY1NDA4MDY5LCJ0eXBlIjoiYWNjZXNzIn0.yRoU7urk4bymoIR8j4YUFmJOkieBrRDskkrWdAwcP6w"

def test_document_listing():
    """Prueba 1: Listar documentos de la mascota"""
    print("\n" + "="*60)
    print("PRUEBA 1: Listando documentos de la mascota")
    print("="*60)
    
    url = f"{BASE_URL}/images/pets/{PET_ID}/documents"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
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
                print(f"   URL: {doc.get('url')}")
                print(f"   Tamaño: {doc.get('file_size_bytes', 0) / 1024:.2f} KB")
            
            return documents
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def test_pdf_download(pdf_url):
    """Prueba 2: Descargar PDF directamente"""
    print("\n" + "="*60)
    print("PRUEBA 2: Descargando PDF directamente")
    print("="*60)
    print(f"URL: {pdf_url}")
    
    try:
        response = requests.get(pdf_url, timeout=30)
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
                return True
            else:
                print(f"   ❌ Advertencia: No parece ser un PDF válido")
                print(f"   Primeros bytes: {response.content[:20]}")
                return False
        else:
            print(f"❌ Error descargando: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_pdf_processing(pdf_url):
    """Prueba 3: Procesar PDF con PyPDF"""
    print("\n" + "="*60)
    print("PRUEBA 3: Procesando PDF con PyPDF")
    print("="*60)
    
    try:
        from pypdf import PdfReader
        import tempfile
        
        # Descargar PDF
        print("📥 Descargando PDF...")
        response = requests.get(pdf_url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error descargando: {response.status_code}")
            return False
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        print(f"✅ PDF guardado temporalmente: {tmp_path}")
        
        # Intentar leer con PyPDF
        print("📖 Leyendo contenido del PDF...")
        reader = PdfReader(tmp_path)
        
        num_pages = len(reader.pages)
        print(f"✅ PDF procesado exitosamente")
        print(f"   Páginas: {num_pages}")
        
        # Extraer texto de la primera página
        if num_pages > 0:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            print(f"   Texto extraído (primeros 200 chars):")
            print(f"   {text[:200]}...")
        
        # Limpiar
        os.unlink(tmp_path)
        print(f"🗑️ Archivo temporal eliminado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando PDF: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_chat_with_documents():
    """Prueba 4: Hacer pregunta con acceso a documentos"""
    print("\n" + "="*60)
    print("PRUEBA 4: Preguntando al chat sobre documentos")
    print("="*60)
    
    url = f"{BASE_URL}/chat/pets/{PET_ID}/ask"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    data = {
        "question": "¿Qué vacunas tiene registradas mi mascota según sus documentos? Por favor, menciona específicamente qué información encuentras en los documentos.",
        "session_id": "diagnostic-test-123"
    }
    
    try:
        print("📤 Enviando pregunta...")
        response = requests.post(url, json=data, headers=headers, timeout=120)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Respuesta recibida:")
            print(f"   has_documents: {result.get('has_documents')}")
            print(f"   source_documents: {len(result.get('source_documents', []))} documentos")
            
            if result.get('source_documents'):
                print(f"\n📚 Documentos fuente usados:")
                for idx, doc in enumerate(result.get('source_documents', []), 1):
                    print(f"   {idx}. Fuente: {doc.get('source', 'unknown')}")
                    print(f"      Página: {doc.get('page', 0)}")
                    print(f"      Contenido: {doc.get('content', '')[:100]}...")
            
            print(f"\n💬 Respuesta del veterinario:")
            print(f"   {result.get('answer', '')[:300]}...")
            
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

def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*60)
    print("🔬 DIAGNÓSTICO DE ACCESO A DOCUMENTOS PDF")
    print("="*60)
    print(f"Pet ID: {PET_ID}")
    print(f"Base URL: {BASE_URL}")
    
    # Prueba 1: Listar documentos
    documents = test_document_listing()
    
    if not documents:
        print("\n❌ No se encontraron documentos. Abortando pruebas.")
        return
    
    # Prueba 2 y 3: Descargar y procesar primer PDF
    first_doc = documents[0]
    pdf_url = first_doc.get('url')
    
    if pdf_url:
        download_ok = test_pdf_download(pdf_url)
        
        if download_ok:
            process_ok = test_pdf_processing(pdf_url)
            
            if not process_ok:
                print("\n⚠️ Advertencia: Hubo problemas procesando el PDF")
    
    # Prueba 4: Chat con documentos
    test_chat_with_documents()
    
    print("\n" + "="*60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    main()