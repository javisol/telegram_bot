"""
Image processing module for Telegram bot.
Handles image uploads, OCR, and base64 encoding for LLM API.
"""
import os
import base64
import logging
from typing import Optional, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Handles image processing for Telegram bot.
    Converts images to base64 and prepares them for LLM API consumption.
    """
    
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
    
    def __init__(self, max_image_size_mb: int = 10):
        """
        Initialize image processor.
        
        Args:
            max_image_size_mb: Maximum allowed image size in MB
        """
        self.max_image_size_bytes = max_image_size_mb * 1024 * 1024
        self.max_image_size_mb = max_image_size_mb
        logger.info(f"Image processor initialized with max size: {max_image_size_mb}MB")
    
    def _get_file_name(self, file: Any) -> str:
        """Helper para extraer de forma segura el nombre del archivo en PTB v20+"""
        if hasattr(file, 'file_name') and file.file_name:
            return file.file_name
        if hasattr(file, 'file_path') and file.file_path:
            return os.path.basename(file.file_path)
        return "image.jpg"
    
    def is_valid_image(self, file: Any) -> tuple[bool, str]:
        """
        Check if the uploaded file is a valid image.
        
        Args:
            file: Telegram file object
            
        Returns:
            Tuple of (is_valid, message)
        """
        if file is None:
            return False, "No file provided"
        
        file_name = self._get_file_name(file)
        file_mime = getattr(file, 'mime_type', '') or ""
        file_size = getattr(file, 'file_size', None)
        
        # Check if file name has supported extension
        has_supported_extension = any(file_name.lower().endswith(ext) for ext in self.SUPPORTED_FORMATS)
        
        # Check MIME type if available (PTB a veces no lo incluye en el objeto File, por eso aceptamos vacío para validar por extensión)
        is_supported_mime = not file_mime or file_mime in [
            'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 
            'image/gif', 'image/bmp', 'image/x-ms-bmp'
        ]
        
        # Check file size
        size_ok = file_size is None or file_size <= self.max_image_size_bytes
        
        if not has_supported_extension:
            return False, f"File format not supported. Expected: {', '.join(self.SUPPORTED_FORMATS)}"
        
        if not is_supported_mime:
            return False, f"File type not supported. MIME type: {file_mime}"
        
        if not size_ok:
            return False, f"File too large. Max size: {self.max_image_size_mb}MB"
        
        return True, "Valid image file"
    
    async def encode_to_base64(self, file: Any) -> str:
        """
        Encode a Telegram file to base64 string.
        (Modificado a 'async' para descargar correctamente el archivo en memoria)
        """
        # Descarga el archivo de Telegram directamente a un buffer en memoria
        file_content = BytesIO()
        await file.download_to_memory(out=file_content)
        file_content.seek(0)
        
        # Read as bytes
        image_bytes = file_content.read()
        
        # Encode to base64 (extraemos solo los bytes puros para mantener compatibilidad con tu estructura)
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        
        return base64_data
    
    def _detect_mime_type(self, file_name: str, file: Any) -> str:
        """Detect MIME type from file name or content."""
        mime_type = getattr(file, 'mime_type', None)
        if mime_type and mime_type.startswith('image/'):
            return mime_type
        
        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
            if file_name.lower().endswith(ext):
                mime_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp'
                }
                return mime_map.get(ext, 'image/jpeg')
        
        return 'image/jpeg'
    
    async def process_image(self, file: Any) -> Dict[str, Any]:
        """
        Process an image file and prepare it for LLM API.
        (Modificado a 'async' debido al procesamiento de red interno)
        """
        # Validate image
        is_valid, message = self.is_valid_image(file)
        if not is_valid:
            logger.warning(f"Invalid image: {message}")
            return {"error": message}
        
        try:
            # Llama de forma asíncrona a la codificación
            base64_pure = await self.encode_to_base64(file)
            
            file_name = self._get_file_name(file)
            mime_type = self._detect_mime_type(file_name, file)
            
            return {
                "base64": base64_pure,
                "mime_type": mime_type,
                "file_name": file_name,
                "size_bytes": getattr(file, 'file_size', 0) or 0
            }
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return {"error": f"Failed to encode image: {str(e)}"}


def prepare_image_message_content(base64_data: str, mime_type: str) -> Dict[str, str]:
    """Prepare image content in the format expected by LLM API."""
    return {
        "type": "image",
        "data": base64_data
    }


def prepare_multimodal_content(text: str, base64_data: str, mime_type: str) -> list:
    """Prepare multimodal content combining text and image."""
    return [
        {"type": "text", "text": text},
        {"type": "image", "data": base64_data}
    ]
