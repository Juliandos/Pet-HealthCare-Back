"""
Servicio para gestión de archivos en AWS S3
Maneja subida, eliminación y obtención de URLs de imágenes
"""
import boto3
import io
import uuid
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
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
            file_content: Contenido binario del archivo
            filename: Nombre original del archivo
            pet_id: ID de la mascota
            optimize: Si debe optimizar la imagen
        
        Returns:
            Dict con información del archivo subido:
            {
                "url": "https://...",
                "key": "pets/uuid/filename.jpg",
                "size": 12345,
                "bucket": "bucket-name"
            }
        """
        # Validar imagen
        is_valid, error = self.validate_image(file_content, filename)
        if not is_valid:
            print(f"❌ Imagen inválida: {error}")
            return None
        
        # Optimizar si está habilitado
        if optimize:
            file_content = self.optimize_image(file_content)
        
        # Generar nombre único
        extension = filename.lower().split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        s3_key = f"pets/{pet_id}/{unique_filename}"
        
        try:
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=f"image/{extension}",
                Metadata={
                    'pet_id': pet_id,
                    'original_filename': filename,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
            
            # Generar URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            
            print(f"✅ Imagen subida exitosamente: {url}")
            
            return {
                "url": url,
                "key": s3_key,
                "size": len(file_content),
                "bucket": self.bucket_name
            }
        
        except ClientError as e:
            print(f"❌ Error subiendo a S3: {str(e)}")
            return None
    
    def delete_image(self, s3_key: str) -> bool:
        """
        Elimina una imagen de S3
        
        Args:
            s3_key: Clave del objeto en S3 (ej: "pets/uuid/image.jpg")
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            print(f"✅ Imagen eliminada: {s3_key}")
            return True
        except ClientError as e:
            print(f"❌ Error eliminando de S3: {str(e)}")
            return False
    
    def get_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Genera una URL firmada temporalmente para acceso privado
        
        Args:
            s3_key: Clave del objeto en S3
            expiration: Tiempo de expiración en segundos (default: 1 hora)
        
        Returns:
            URL firmada o None si hay error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"❌ Error generando URL firmada: {str(e)}")
            return None
    
    def upload_pet_profile_photo(
        self,
        file_content: bytes,
        filename: str,
        pet_id: str
    ) -> Optional[dict]:
        """
        Sube la foto de perfil de una mascota
        
        Args:
            file_content: Contenido binario del archivo
            filename: Nombre original del archivo
            pet_id: ID de la mascota
        
        Returns:
            Dict con información del archivo subido
        """
        return self.upload_image(file_content, filename, pet_id, optimize=True)
    
    def upload_pet_gallery_photo(
        self,
        file_content: bytes,
        filename: str,
        pet_id: str
    ) -> Optional[dict]:
        """
        Sube una foto a la galería de una mascota
        
        Args:
            file_content: Contenido binario del archivo
            filename: Nombre original del archivo
            pet_id: ID de la mascota
        
        Returns:
            Dict con información del archivo subido
        """
        return self.upload_image(file_content, filename, pet_id, optimize=True)
    
    def list_pet_photos(self, pet_id: str) -> list[dict]:
        """
        Lista todas las fotos de una mascota
        
        Args:
            pet_id: ID de la mascota
        
        Returns:
            Lista de diccionarios con información de las fotos
        """
        try:
            prefix = f"pets/{pet_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            photos = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    photos.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'url': f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{obj['Key']}"
                    })
            
            return photos
        except ClientError as e:
            print(f"❌ Error listando fotos: {str(e)}")
            return []
    
    def delete_pet_photos(self, pet_id: str) -> bool:
        """
        Elimina todas las fotos de una mascota
        
        Args:
            pet_id: ID de la mascota
        
        Returns:
            True si se eliminaron correctamente
        """
        try:
            # Listar todas las fotos
            photos = self.list_pet_photos(pet_id)
            
            if not photos:
                return True
            
            # Eliminar cada foto
            objects_to_delete = [{'Key': photo['key']} for photo in photos]
            
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': objects_to_delete}
            )
            
            print(f"✅ Eliminadas {len(photos)} fotos de mascota {pet_id}")
            return True
        except ClientError as e:
            print(f"❌ Error eliminando fotos: {str(e)}")
            return False

# Instancia global del servicio
s3_service = S3Service()