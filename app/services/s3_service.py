"""
Servicio para gestión de archivos en AWS S3
Maneja subida, eliminación y obtención de URLs de imágenes
"""
import boto3
import io
import uuid
from typing import Optional, BinaryIO
from datetime import datetime
from PIL import Image
from botocore.exceptions import ClientError
from app.config import settings

class S3Service:
    """Servicio para operaciones con AWS S3"""
    
    def __init__(self):
        """Inicializa el cliente de S3"""
        # Configurar cliente S3
        s3_config = {
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
            'region_name': settings.AWS_REGION
        }
        
        # Si hay endpoint URL (para servicios compatibles con S3)
        if settings.AWS_S3_ENDPOINT_URL:
            s3_config['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL
        
        self.s3_client = boto3.client('s3', **s3_config)
        self.bucket_name = settings.AWS_S3_BUCKET
    
    def validate_image(self, file_content: bytes, filename: str) -> tuple[bool, str]:
        """
        Valida una imagen antes de subirla
        
        Args:
            file_content: Contenido binario del archivo
            filename: Nombre del archivo
        
        Returns:
            (is_valid, error_message)
        """
        # Verificar tamaño
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > settings.MAX_IMAGE_SIZE_MB:
            return False, f"La imagen excede el tamaño máximo de {settings.MAX_IMAGE_SIZE_MB}MB"
        
        # Verificar extensión
        extension = filename.lower().split('.')[-1]
        if extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Extensión no permitida. Use: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        
        # Verificar que sea una imagen válida
        try:
            img = Image.open(io.BytesIO(file_content))
            img.verify()
            return True, ""
        except Exception as e:
            return False, f"Archivo no es una imagen válida: {str(e)}"
    
    def optimize_image(self, file_content: bytes, max_width: int = 1200) -> bytes:
        """
        Optimiza una imagen redimensionándola y comprimiéndola
        
        Args:
            file_content: Contenido binario de la imagen
            max_width: Ancho máximo en píxeles
        
        Returns:
            Imagen optimizada en bytes
        """
        try:
            img = Image.open(io.BytesIO(file_content))
            
            # Convertir RGBA a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensionar si es necesario
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Guardar optimizada
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"⚠️ Error optimizando imagen: {str(e)}")
            return file_content
    
    def upload_image(
        self,
        file_content: bytes,
        filename: str,
        pet_id: str,
        optimize: bool = True
    ) -> Optional[dict]:
        """
        Sube una imagen a S3
        
        Args:
            file_content: Contenido binario