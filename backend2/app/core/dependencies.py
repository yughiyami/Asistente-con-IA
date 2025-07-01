"""
Dependencias inyectables para FastAPI.
Centraliza la creación y gestión de servicios.
"""

from functools import lru_cache
from typing import Generator, Dict
import logging

from app.services.gemini_service import GeminiService
from app.services.serper_service import SerperService
from app.services.redis_service import RedisService
from app.services.document_service import DocumentService
from app.services.game_service import GameService
from app.core.config import get_settings, Settings

logger = logging.getLogger(__name__)


# Servicios singleton cacheados
@lru_cache()
def get_gemini_service() -> GeminiService:
    """
    Obtiene una instancia singleton del servicio Gemini.
    
    Returns:
        Instancia de GeminiService
    """
    logger.info("Inicializando servicio Gemini")
    return GeminiService()


@lru_cache()
def get_serper_service() -> SerperService:
    """
    Obtiene una instancia singleton del servicio Serper.
    
    Returns:
        Instancia de SerperService
    """
    logger.info("Inicializando servicio Serper")
    return SerperService()


@lru_cache()
def get_redis_service() -> RedisService:
    """
    Obtiene una instancia singleton del servicio Redis.
    
    Returns:
        Instancia de RedisService
    """
    logger.info("Inicializando servicio Redis")
    return RedisService()


@lru_cache()
def get_document_service() -> DocumentService:
    """
    Obtiene una instancia singleton del servicio de documentos.
    
    Returns:
        Instancia de DocumentService
    """
    logger.info("Inicializando servicio de documentos")
    return DocumentService()


def get_game_service() -> GameService:
    """
    Obtiene una instancia del servicio de juegos.
    
    No se cachea porque depende de otros servicios que podrían cambiar.
    
    Returns:
        Nueva instancia de GameService
    """
    gemini = get_gemini_service()
    redis = get_redis_service()
    return GameService(gemini, redis)


# Dependencias de configuración
def get_settings_dependency() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    
    Returns:
        Instancia de Settings
    """
    return get_settings()


# Limpieza de recursos
def cleanup_services():
    """
    Limpia y cierra conexiones de todos los servicios.
    
    Debe llamarse al cerrar la aplicación.
    """
    logger.info("Limpiando servicios...")
    
    # Limpiar cachés de servicios singleton
    get_gemini_service.cache_clear()
    get_serper_service.cache_clear()
    get_redis_service.cache_clear()
    get_document_service.cache_clear()
    
    logger.info("Servicios limpiados correctamente")


# Verificación de salud de servicios
async def check_services_health() -> Dict[str, bool]:
    """
    Verifica el estado de salud de todos los servicios.
    
    Returns:
        Diccionario con el estado de cada servicio
    """
    health_status = {
        "gemini": False,
        "serper": False,
        "redis": False,
        "documents": False
    }
    
    try:
        # Verificar Gemini
        gemini = get_gemini_service()
        # Hacer una llamada simple para verificar
        health_status["gemini"] = gemini.model is not None
    except Exception as e:
        logger.error(f"Error verificando Gemini: {str(e)}")
    
    try:
        # Verificar Serper
        serper = get_serper_service()
        health_status["serper"] = bool(serper.api_key)
    except Exception as e:
        logger.error(f"Error verificando Serper: {str(e)}")
    
    try:
        # Verificar Redis
        redis = get_redis_service()
        redis.redis_client.ping()
        health_status["redis"] = True
    except Exception as e:
        logger.error(f"Error verificando Redis: {str(e)}")
    
    try:
        # Verificar servicio de documentos
        docs = get_document_service()
        health_status["documents"] = docs.documents_path.exists()
    except Exception as e:
        logger.error(f"Error verificando documentos: {str(e)}")
    
    return health_status