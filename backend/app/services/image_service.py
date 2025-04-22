import os
import httpx
import json
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageSearchService:
    def __init__(self):
        self.api_key = settings.IMAGE_SEARCH_API_KEY
        self.image_cache = {}  # Simple cache en memoria para reutilizar resultados
    
    async def search_images(self, query: str, num_images: int = 3) -> List[Dict[str, Any]]:
        """Busca imágenes relacionadas con una consulta usando Serper API"""
        # Versión simplificada - en una implementación real usarías una API de búsqueda de imágenes
        
        # Comprobar caché
        cache_key = f"{query}_{num_images}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        try:
            # Ejemplo con Serper API (se necesita una clave API real)
            url = "https://google.serper.dev/images"
            payload = json.dumps({
                "q": f"computer architecture {query}",
                "gl": "us",
                "hl": "en",
                "num": num_images
            })
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    images = []
                    
                    for item in data.get("images", [])[:num_images]:
                        images.append({
                            "url": item.get("imageUrl"),
                            "alt_text": item.get("title", query),
                            "source": item.get("source")
                        })
                    
                    # Guardar en caché
                    self.image_cache[cache_key] = images
                    return images
                else:
                    logger.error(f"Error al buscar imágenes: {response.status_code} - {response.text}")
                    return self._get_fallback_images(query, num_images)
        
        except Exception as e:
            logger.error(f"Error en search_images: {str(e)}")
            return self._get_fallback_images(query, num_images)
    
    def _get_fallback_images(self, query: str, num_images: int = 3) -> List[Dict[str, Any]]:
        """Proporciona imágenes de respaldo en caso de error"""
        # En una implementación real podrías tener imágenes locales o usar otra fuente alternativa
        
        # Conjunto predefinido de URLs de imágenes para arquitectura de computadoras
        fallback_images = [
            {
                "url": "https://placeholder.com/640x480?text=CPU+Architecture",
                "alt_text": "Arquitectura CPU",
                "source": "Placeholder Image"
            },
            {
                "url": "https://placeholder.com/640x480?text=Computer+Memory",
                "alt_text": "Memoria de computadora",
                "source": "Placeholder Image"
            },
            {
                "url": "https://placeholder.com/640x480?text=Cache+Memory",
                "alt_text": "Memoria caché",
                "source": "Placeholder Image"
            },
            {
                "url": "https://placeholder.com/640x480?text=Computer+Architecture",
                "alt_text": "Arquitectura de computadoras",
                "source": "Placeholder Image"
            }
        ]
        
        return fallback_images[:num_images]

# Crear instancia global del servicio
image_service = ImageSearchService()