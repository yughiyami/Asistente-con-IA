"""
Esquemas Pydantic para las solicitudes y respuestas del modo Chat/Repaso.
Estos modelos se utilizan para validar los datos de entrada y salida de la API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, AnyHttpUrl


class ImageInfo(BaseModel):
    """
    Información de una imagen sugerida.
    
    Attributes:
        url: URL de la imagen
        description: Descripción o título de la imagen
        alt_text: Texto alternativo para accesibilidad
    """
    url: AnyHttpUrl = Field(..., description="URL de la imagen")
    description: str = Field(..., description="Descripción o título de la imagen")
    alt_text: Optional[str] = Field(None, description="Texto alternativo para accesibilidad")


class ChatRequest(BaseModel):
    """
    Solicitud para el modo chat/repaso.
    
    Attributes:
        query: La consulta o pregunta del usuario
        context_ids: Lista opcional de IDs de documentos PDF para proporcionar contexto
        history_id: ID opcional de la conversación para mantener contexto histórico
    """
    query: str = Field(..., 
                       description="Pregunta o consulta sobre arquitectura de computadoras",
                       example="¿Qué es la arquitectura Harvard?")
    context_ids: Optional[List[str]] = Field(default=[],
                                           description="IDs de los PDFs a considerar como contexto",
                                           example=["cpu_architecture.pdf", "memory_systems.pdf"])
    history_id: Optional[str] = Field(default=None,
                                    description="ID de la conversación para mantener contexto histórico")


class Reference(BaseModel):
    """
    Representación de una referencia bibliográfica.
    
    Attributes:
        title: Título del documento o recurso
        authors: Autores del documento
        year: Año de publicación
        source: Fuente o editorial
        url: URL opcional si está disponible en línea
    """
    title: str = Field(..., example="Computer Organization and Design: The Hardware/Software Interface")
    authors: str = Field(..., example="Patterson, D. A., & Hennessy, J. L.")
    year: int = Field(..., example=2017)
    source: str = Field(..., example="Morgan Kaufmann")
    url: Optional[AnyHttpUrl] = Field(default=None)
    
    def __str__(self) -> str:
        """Formato de cita académica para la referencia."""
        citation = f"{self.authors} ({self.year}). {self.title}. {self.source}"
        if self.url:
            citation += f". URL: {self.url}"
        return citation


class ChatResponse(BaseModel):
    """
    Respuesta para el modo chat/repaso.
    
    Attributes:
        message: Texto de respuesta generado por el LLM
        images: Lista de URLs de imágenes relevantes
        references: Lista de referencias bibliográficas
        history_id: ID de la conversación para futuras interacciones
    """
    message: str = Field(..., 
                         description="Respuesta generada para la consulta del usuario")
    images: List[str] = Field(default=[],
                             description="URLs de imágenes relevantes")
    references: List[Reference] = Field(default=[],
                                      description="Referencias bibliográficas utilizadas")
    history_id: str = Field(..., 
                            description="ID para seguimiento de la conversación")

    class Config:
        """Configuración del esquema."""
        schema_extra = {
            "example": {
                "message": "La arquitectura Harvard es un diseño de computadora con rutas físicamente separadas para instrucciones y datos...",
                "images": ["https://example.com/images/harvard_architecture.jpg"],
                "references": [
                    {
                        "title": "Computer Organization and Design: The Hardware/Software Interface",
                        "authors": "Patterson, D. A., & Hennessy, J. L.",
                        "year": 2017,
                        "source": "Morgan Kaufmann",
                        "url": None
                    }
                ],
                "history_id": "chat_session_123456"
            }
        }