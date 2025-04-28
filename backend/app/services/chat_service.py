"""
Servicio para el modo Chat/Repaso.
Gestiona las consultas de los usuarios y genera respuestas educativas.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional

from app.services.llm import llm_service
from app.services.pdf_service import pdf_service
from app.schemas.chat import ChatResponse, Reference

# Configurar logger
logger = logging.getLogger(__name__)


class ChatService:
    """
    Servicio para gestionar el modo Chat/Repaso.
    
    Proporciona métodos para:
    - Procesar consultas de usuario
    - Generar respuestas educativas
    - Integrar información de documentos PDF
    - Sugerir imágenes relevantes
    """
    
    def __init__(self):
        """Inicializa el servicio de chat."""
        self.chat_sessions = {}
    
    async def process_query(
        self, 
        query: str, 
        context_ids: Optional[List[str]] = None,
        history_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Procesa una consulta del usuario y genera una respuesta educativa.
        
        Args:
            query: Consulta o pregunta del usuario
            context_ids: Lista opcional de IDs de documentos PDF para proporcionar contexto
            history_id: ID opcional de la conversación para mantener contexto histórico
            
        Returns:
            Respuesta completa con mensaje, imágenes y referencias
        """
        try:
            # Generar ID de conversación (nuevo o continuar el existente)
            session_id = history_id or f"chat_{uuid.uuid4().hex}"
            
            # Obtener contenido relevante de los PDFs
            context = ""
            if context_ids:
                # El usuario especificó documentos concretos
                relevant_content = await pdf_service.search_relevant_content(
                    query=query, 
                    doc_ids=context_ids,
                    max_results=5
                )
                
                # Construir contexto a partir del contenido relevante
                if relevant_content:
                    context = "Información relevante de los documentos del curso:\n\n"
                    for i, item in enumerate(relevant_content, 1):
                        context += f"[Documento {i}: {item['doc_title']}]\n"
                        context += f"{item['content']}\n\n"
            
            # Obtener respuesta del LLM con el modelo de chat
            llm_response = await llm_service.get_chat_response(
                message=query,
                session_id=session_id,
                mode="chat"
            )
            
            # Extraer texto de respuesta e imágenes sugeridas
            text_response = llm_response.get("text", "")
            image_queries = llm_response.get("image_queries", [])
            
            # Convertir consultas de imágenes a URLs (en una implementación real, se generarían o buscarían)
            images = []
            for img_query in image_queries:
                # Simulación - en producción se usaría un servicio real
                images.append(f"https://example.com/images/computer_architecture/{img_query['query'].replace(' ', '_')}.jpg")
            
            # Generar referencias bibliográficas
            # En una implementación real, estas se extraerían de los metadatos de los PDFs
            references = [
                Reference(
                    title="Computer Organization and Design: The Hardware/Software Interface",
                    authors="Patterson, D. A., & Hennessy, J. L.",
                    year=2017,
                    source="Morgan Kaufmann"
                ),
                Reference(
                    title="Computer Architecture: A Quantitative Approach",
                    authors="Hennessy, J. L., & Patterson, D. A.",
                    year=2019,
                    source="Morgan Kaufmann"
                ),
            ]
            
            # Construir la respuesta completa
            return ChatResponse(
                message=text_response,
                images=images,
                references=references,
                history_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error en process_query: {str(e)}")
            
            # Proporcionar una respuesta genérica en caso de error
            return ChatResponse(
                message="Lo siento, ha ocurrido un error al procesar tu consulta. Por favor, intenta de nuevo con una pregunta diferente.",
                images=[],
                references=[],
                history_id=history_id or f"chat_{uuid.uuid4().hex}"
            )
    
    async def get_chat_history(self, history_id: str) -> List[Dict[str, Any]]:
        """
        Recupera el historial de conversación.
        
        Args:
            history_id: ID de la conversación
            
        Returns:
            Lista de mensajes intercambiados
        """
        # En una implementación real, esto recuperaría mensajes de una base de datos
        # Por ahora, devolvemos una lista vacía
        return []
    
    async def reset_chat(self, history_id: str) -> bool:
        """
        Reinicia una conversación existente.
        
        Args:
            history_id: ID de la conversación a reiniciar
            
        Returns:
            True si se reinició correctamente, False en caso contrario
        """
        # En una implementación real, esto limpiaría el historial en la base de datos
        # Por ahora, verificamos si el ID está en las sesiones de chat del LLM
        if history_id in llm_service.chat_sessions:
            del llm_service.chat_sessions[history_id]
            return True
        return False


# Instancia global del servicio
chat_service = ChatService()