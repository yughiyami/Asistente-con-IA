"""
Servicio para interactuar con Serper API.
Maneja búsqueda y obtención de imágenes relevantes.
"""

import httpx
import logging
from typing import List, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class SerperService:
    """Servicio para búsqueda de imágenes con Serper"""
    
    def __init__(self):
        """Inicializa el servicio con configuración"""
        self.api_key = settings.serper_api_key
        self.base_url = "https://google.serper.dev"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def search_images(
        self, 
        query: str, 
        num_images: int = 3,
        safe_search: bool = True
    ) -> List[Dict[str, str]]:
        """
        Busca imágenes relevantes para el query dado.
        
        Args:
            query: Término de búsqueda
            num_images: Número de imágenes a retornar
            safe_search: Activar búsqueda segura
            
        Returns:
            Lista de diccionarios con URL y título de imágenes
        """
        # Agregar contexto educativo al query
        enhanced_query = f"{query} computer architecture educational diagram"
        
        payload = {
            "q": enhanced_query,
            "num": num_images,
            "gl": "us",
            "hl": "es",
            "safe": "active" if safe_search else "off",
            "tbm": "isch",  # Búsqueda de imágenes
            "engine": "google"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/images",
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_image_results(data.get("images", []))
                else:
                    logger.error(f"Error en Serper API: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error buscando imágenes: {str(e)}")
            return []
    
    async def get_diagram_images(self, concept: str) -> List[Dict[str, str]]:
        """
        Busca diagramas específicos para conceptos de arquitectura.
        
        Args:
            concept: Concepto de arquitectura de computadoras
            
        Returns:
            Lista de imágenes de diagramas
        """
        # Queries especializados para diagramas técnicos
        queries = [
            f"{concept} block diagram",
            f"{concept} architecture diagram",
            f"{concept} circuit schematic"
        ]
        
        all_images = []
        for query in queries:
            images = await self.search_images(query, num_images=1)
            all_images.extend(images)
        
        return all_images[:3]  # Máximo 3 imágenes
    
    def _process_image_results(self, images: List[Dict]) -> List[Dict[str, str]]:
        """
        Procesa los resultados de búsqueda de imágenes.
        
        Args:
            images: Lista cruda de resultados de Serper
            
        Returns:
            Lista procesada con formato estándar
        """
        processed = []
        
        for img in images:
            # Filtrar imágenes por calidad y relevancia
            if self._is_valid_image(img):
                processed.append({
                    "url": img.get("imageUrl", ""),
                    "title": img.get("title", ""),
                    "source": img.get("source", "serper")
                })
        
        return processed
    
    def _is_valid_image(self, image: Dict) -> bool:
        """
        Valida si una imagen es apropiada para uso educativo.
        
        Args:
            image: Datos de la imagen
            
        Returns:
            True si la imagen es válida
        """
        # Validar que tenga URL
        if not image.get("imageUrl"):
            return False
        
        url = image["imageUrl"].lower()
        
        # Filtrar por extensiones válidas
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        if not any(ext in url for ext in valid_extensions):
            return False
        
        # Filtrar dominios problemáticos
        blocked_domains = ['pinterest', 'instagram', 'facebook']
        if any(domain in url for domain in blocked_domains):
            return False
        
        # Preferir fuentes educativas
        educational_domains = ['edu', 'wikipedia', 'academic', 'university']
        if any(domain in url for domain in educational_domains):
            return True
        
        return True
    
    async def get_concept_visualization(
        self, 
        concept: str,
        visualization_type: str = "diagram"
    ) -> Optional[Dict[str, str]]:
        """
        Obtiene una visualización específica para un concepto.
        
        Args:
            concept: Concepto a visualizar
            visualization_type: Tipo de visualización (diagram, flowchart, etc.)
            
        Returns:
            Diccionario con información de la imagen o None
        """
        query = f"{concept} {visualization_type} computer architecture"
        images = await self.search_images(query, num_images=1)
        
        return images[0] if images else None