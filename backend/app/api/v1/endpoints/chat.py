"""
Endpoints para el modo Chat/Repaso.
Gestiona las solicitudes de chat y generación de respuestas educativas.
"""

import uuid
import logging
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.schemas.chat import ChatRequest, ChatResponse, Reference
from app.services.llm import llm_service
from app.services.pdf_service import pdf_service
from app.services.image_service import image_service
from app.config import settings
from app.api import deps

# Configurar logger
logger = logging.getLogger(__name__)

# Configurar router
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def generate_chat_response(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
) -> ChatResponse:
    """
    Genera una respuesta educativa para una consulta sobre arquitectura de computadoras.
    
    - Utiliza el contexto de los PDFs especificados
    - Genera imágenes relevantes utilizando Serper.dev
    - Incluye referencias a fuentes académicas
    
    Parameters:
    - **request**: Consulta y parámetros de contexto
    
    Returns:
    - **ChatResponse**: Respuesta completa con mensaje, imágenes y referencias
    """
    try:
        # Obtener contenido relevante de los PDFs
        context = ""
        
        if request.context_ids:
            # El usuario especificó documentos concretos
            relevant_content = await pdf_service.search_relevant_content(
                query=request.query, 
                doc_ids=request.context_ids,
                max_results=5
            )
        else:
            # Buscar en todos los documentos disponibles
            relevant_content = await pdf_service.search_relevant_content(
                query=request.query,
                max_results=5
            )
        
        # Construir contexto a partir del contenido relevante
        if relevant_content:
            context = "Información relevante de los documentos del curso:\n\n"
            for i, item in enumerate(relevant_content, 1):
                context += f"[Documento {i}: {item['doc_title']}]\n"
                context += f"{item['content']}\n\n"
        
        # Generar ID de conversación (nuevo o continuar el existente)
        history_id = request.history_id or f"chat_{uuid.uuid4().hex}"
        
        # Construir prompt completo para Gemini
        prompt = f"""
        Responde a esta pregunta sobre arquitectura de computadoras: {request.query}
        
        Proporciona información precisa y detallada, adaptando tu explicación para un estudiante universitario.
        Si es relevante, indica qué imágenes serían útiles incluir, marcándolas con IMAGEN_SUGERIDA: [descripción].
        Limítate a sugerir máximo 3 imágenes realmente importantes para comprender el tema.
        
        Al final de tu respuesta, incluye entre 2-3 referencias bibliográficas relevantes con el formato:
        REFERENCIA: [título] | [autores] | [año] | [editorial]
        """
        
        # Usar el contexto como parte del sistema si está disponible
        if context:
            prompt = f"{prompt}\n\nUtiliza esta información para tu respuesta:\n{context}"
        
        # Llamar al LLM de Gemini utilizando el servicio de chat
        chat_response = await llm_service.get_chat_response(
            message=prompt,
            session_id=history_id,
            mode="chat"
        )
        
        # Extraer texto y sugerencias de imágenes
        text_response = chat_response.get("text", "")
        image_queries = chat_response.get("image_queries", [])
        
        # Procesar imágenes usando serper.dev
        images = []
        if image_queries:
            # Usar el servicio de imágenes para buscar imágenes basadas en las sugerencias
            images = await image_service.get_images_for_suggestions(
                image_queries, 
                max_per_suggestion=1
            )
        
        # Si no hay sugerencias o falló la búsqueda, buscar una imagen genérica basada en la consulta
        if not images:
            # Extraer frase clave de la consulta para buscar una imagen
            key_phrase = request.query
            if len(key_phrase) > 50:  # Si la consulta es muy larga, acortarla
                key_phrase = key_phrase[:50]
            
            # Buscar imágenes con la frase clave
            images = await image_service.search_images(key_phrase, 3)
        
        # Limitar a máximo 3 imágenes
        images = images[:settings.MAX_IMAGES_PER_RESPONSE]

        # Extraer referencias bibliográficas del texto
        references = []
        ref_pattern = r"REFERENCIA:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d{4})\s*\|\s*(.*?)(?:\n|$)"
        ref_matches = re.findall(ref_pattern, text_response)
        
        # Limpiar las referencias del texto de respuesta
        text_response = re.sub(r"REFERENCIA:.*?(?:\n|$)", "", text_response).strip()
        
        # Crear objetos de referencias
        for match in ref_matches:
            if len(match) >= 4:
                references.append(Reference(
                    title=match[0].strip(),
                    authors=match[1].strip(),
                    year=int(match[2].strip()),
                    source=match[3].strip()
                ))
        
        # Si no se extrajeron referencias, proporcionar algunas predeterminadas
        if not references:
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
        
        # Agregar tarea en segundo plano para registrar la consulta
        background_tasks.add_task(
            lambda: logger.info(f"Chat request: {request.query}, history_id: {history_id}")
        )
        
        return ChatResponse(
            message=text_response,
            images=images,
            references=references,
            history_id=history_id
        )
        
    except Exception as e:
        logger.error(f"Error al generar respuesta de chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al generar la respuesta. Por favor, inténtalo de nuevo."
        )


@router.get("/documents", response_model=List[dict])
async def list_available_documents():
    """
    Lista todos los documentos disponibles para contexto.
    
    Returns:
    - Lista de documentos con ID y título
    """
    try:
        documents = pdf_service.list_available_documents()
        # Filtrar solo la información necesaria para el frontend
        return [{"id": doc["id"], "title": doc["title"]} for doc in documents]
        
    except Exception as e:
        logger.error(f"Error al listar documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la lista de documentos"
        )