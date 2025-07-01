"""
Router para endpoints de chat con IA.
Maneja conversaciones y búsqueda de documentos.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List , Dict
import logging

from app.schemas.chat import (
    ChatRequest, ChatResponse, Document
)
from app.services.gemini_service import GeminiService
from app.services.serper_service import SerperService
from app.services.redis_service import RedisService
from app.services.document_service import DocumentService
from app.core.dependencies import (
    get_gemini_service,
    get_serper_service,
    get_redis_service,
    get_document_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def generate_chat_response(
    request: ChatRequest,
    gemini: GeminiService = Depends(get_gemini_service),
    serper: SerperService = Depends(get_serper_service),
    redis: RedisService = Depends(get_redis_service),
    documents: DocumentService = Depends(get_document_service)
) -> ChatResponse:
    """
    Genera una respuesta educativa para una consulta sobre arquitectura de computadoras.
    
    - Utiliza el contexto de los PDFs especificados
    - Genera imágenes relevantes utilizando Serper
    - Incluye referencias a fuentes académicas
    """
    try:
        # Obtener o crear sesión
        if request.history_id:
            session = await redis.get_chat_session(request.history_id)
            if not session:
                # Si no existe la sesión, crear una nueva
                history_id = await redis.create_chat_session()
                history = []
            else:
                history_id = request.history_id
                history = session.get("messages", [])
        else:
            # Nueva sesión
            history_id = await redis.create_chat_session()
            history = []
        
        # Obtener contexto de documentos si se especificaron
        context = None
        references = []
        
        if request.context_ids:
            context = await documents.get_document_content(request.context_ids)
            
            # Crear referencias para los documentos usados
            for doc_id in request.context_ids:
                if doc_id in documents.sample_documents:
                    doc_info = documents.sample_documents[doc_id]
                    references.append({
                        "title": doc_info["title"],
                        "source": f"Documento interno: {doc_id}",
                        "url": None,
                        "page": None
                    })
        
        # Agregar pregunta del usuario al historial
        await redis.add_chat_message(history_id, "user", request.query)
        
        # Generar respuesta con Gemini
        ai_response = await gemini.generate_chat_response(
            query=request.query,
            context=context,
            history=history
        )
        
        # Buscar imágenes relevantes con Serper
        images = []
        
        # Extraer conceptos clave para buscar imágenes
        key_concepts = _extract_key_concepts(request.query)
        for concept in key_concepts[:2]:  # Máximo 2 conceptos
            concept_images = await serper.get_diagram_images(concept)
            images.extend(concept_images)
        
        # Limitar a 3 imágenes máximo
        images = images[:3]
        
        # Agregar respuesta de la IA al historial
        await redis.add_chat_message(history_id, "assistant", ai_response)
        
        # Agregar referencias académicas estándar si no hay documentos
        if not references:
            references = _get_default_references(request.query)
        
        return ChatResponse(
            message=ai_response,
            images=images,
            references=references,
            history_id=history_id
        )
        
    except Exception as e:
        logger.error(f"Error generando respuesta de chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}"
        )


@router.get("/documents", response_model=List[Document])
async def list_available_documents(
    documents: DocumentService = Depends(get_document_service)
) -> List[Document]:
    """
    Lista todos los documentos disponibles para contexto.
    
    Returns:
        Lista de documentos con ID, título, páginas y tamaño
    """
    try:
        docs = await documents.list_documents()
        return docs
        
    except Exception as e:
        logger.error(f"Error listando documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo lista de documentos: {str(e)}"
        )


def _extract_key_concepts(query: str) -> List[str]:
    """
    Extrae conceptos clave de la consulta para búsqueda de imágenes.
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Lista de conceptos clave
    """
    # Conceptos comunes en arquitectura de computadoras
    key_terms = [
        "cpu", "procesador", "memoria", "cache", "caché", "ram", "rom",
        "pipeline", "registros", "alu", "bus", "microprocesador",
        "instrucciones", "assembly", "ensamblador", "x86", "arm",
        "risc", "cisc", "harvard", "von neumann", "compuertas",
        "flip-flop", "multiplexor", "demultiplexor", "sumador",
        "interrupciones", "dma", "virtual", "paginación", "segmentación",
        "stack", "pila", "heap", "direccionamiento", "modos"
    ]
    
    query_lower = query.lower()
    found_concepts = []
    
    # Buscar términos clave en la consulta
    for term in key_terms:
        if term in query_lower:
            found_concepts.append(term)
    
    # Si no se encontraron términos específicos, usar términos generales
    if not found_concepts:
        if "arquitectura" in query_lower:
            found_concepts.append("computer architecture")
        elif "computadora" in query_lower or "ordenador" in query_lower:
            found_concepts.append("computer organization")
        else:
            found_concepts.append("computer architecture diagram")
    
    return found_concepts


def _get_default_references(query: str) -> List[Dict]:
    """
    Obtiene referencias académicas por defecto basadas en la consulta.
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Lista de referencias académicas relevantes
    """
    # Referencias estándar por tema
    references_db = {
        "pipeline": [
            {
                "title": "Computer Organization and Design",
                "source": "Patterson & Hennessy",
                "url": None,
                "page": 251
            }
        ],
        "cache": [
            {
                "title": "Computer Architecture: A Quantitative Approach",
                "source": "Hennessy & Patterson",
                "url": None,
                "page": 78
            }
        ],
        "memoria": [
            {
                "title": "Structured Computer Organization",
                "source": "Andrew S. Tanenbaum",
                "url": None,
                "page": 145
            }
        ],
        "default": [
            {
                "title": "Computer Organization and Architecture",
                "source": "William Stallings",
                "url": None,
                "page": None
            }
        ]
    }
    
    # Buscar referencias relevantes
    query_lower = query.lower()
    
    for topic, refs in references_db.items():
        if topic in query_lower:
            return refs
    
    # Retornar referencias por defecto
    return references_db["default"]