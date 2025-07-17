"""
Esquemas para el módulo de chat con Gemini.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from .base import ImageData, ProcessingMode, Reference

class ProcessingModeRequest(BaseModel):
    """Solicitud para cambiar el modo de procesamiento"""
    mode: ProcessingMode = Field(..., description="Modo de procesamiento: knowledge_base o free")

class ChatRequest(BaseModel):
    """Solicitud de chat"""
    query: str = Field(..., min_length=1, description="Pregunta o consulta sobre arquitectura de computadoras")
    context_ids: List[str] = Field(default=[], description="IDs de los PDFs a considerar como contexto")
    history_id: Optional[str] = Field(None, description="ID de la conversación para mantener contexto histórico")


class ChatResponse(BaseModel):
    """Respuesta del chat"""
    message: str = Field(..., description="Respuesta generada por la IA")
    images: List[ImageData] = Field(default=[], description="Imágenes relacionadas con la respuesta")
    references: List[Reference] = Field(default=[], description="Referencias académicas utilizadas")
    history_id: str = Field(..., description="ID de la conversación para futuras referencias")


class Document(BaseModel):
    """Documento disponible para contexto"""
    id: str = Field(..., description="Identificador único del documento")
    title: str = Field(..., description="Título del documento")
    pages: int = Field(..., description="Número de páginas")
    size_mb: float = Field(..., description="Tamaño en megabytes")


class ConversationHistory(BaseModel):
    """Historial de conversación"""
    history_id: str
    messages: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime