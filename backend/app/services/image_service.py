"""
Servicio para búsqueda de imágenes utilizando la API de serper.dev.
Proporciona funcionalidades para encontrar imágenes relevantes basadas en consultas.
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import settings

# Configurar logger
logger = logging.getLogger(__name__)

class ImageService:
    """
    Servicio para buscar imágenes utilizando serper.dev.
    
    Proporciona métodos para:
    - Buscar imágenes basadas en consultas de texto
    - Extraer URLs de imágenes de las respuestas
    """
    
    def __init__(self):
        """Inicializa el servicio de imágenes con la configuración global."""
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/images"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def search_images(self, query: str, num_results: int = 3) -> List[str]:
        """
        Busca imágenes utilizando la API de serper.dev.
        
        Args:
            query: Consulta de búsqueda
            num_results: Número máximo de resultados a devolver
            
        Returns:
            Lista de URLs de imágenes
        """
        try:
            # Preparar la consulta - añadir contexto de arquitectura de computadoras
            search_query = f"{query} computer architecture diagram"
            
            # Configurar la solicitud
            payload = {
                "q": search_query,
                "gl": "us",
                "hl": "en"
            }
            
            # Realizar la solicitud
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                search_results = response.json()
            
            # Extraer URLs de imágenes
            image_urls = []
            if "images" in search_results:
                for image in search_results["images"][:num_results]:
                    if "imageUrl" in image:
                        image_urls.append(image["imageUrl"])
            
            logger.info(f"Found {len(image_urls)} images for query: {query}")
            return image_urls
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching images: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            return []
            
        except Exception as e:
            logger.error(f"Error searching images: {str(e)}")
            return []
    
    async def get_images_for_suggestions(self, suggestions: List[Dict[str, str]], max_per_suggestion: int = 1) -> List[str]:
        """
        Obtiene imágenes para una lista de sugerencias.
        
        Args:
            suggestions: Lista de sugerencias de imágenes (con campo 'query')
            max_per_suggestion: Máximo número de imágenes por sugerencia
            
        Returns:
            Lista de URLs de imágenes
        """
        all_images = []
        
        for suggestion in suggestions:
            query = suggestion.get("query", "")
            if query:
                images = await self.search_images(query, max_per_suggestion)
                all_images.extend(images)
                
                # Limitar el número total de imágenes
                if len(all_images) >= 3:
                    break
        
        return all_images[:3]  # Devolver como máximo 3 imágenes


# Instancia global del servicio
image_service = ImageService()