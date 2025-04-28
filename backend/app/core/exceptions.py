"""
Manejo centralizado de excepciones para la aplicación.
Define excepciones personalizadas y configura manejadores globales.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configurar logger
logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Excepción base para errores específicos de la aplicación.
    
    Attributes:
        status_code: Código HTTP a devolver
        detail: Mensaje detallado de error
        headers: Cabeceras HTTP adicionales (opcional)
    """
    
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        headers: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class LLMServiceException(AppException):
    """Excepción para errores en el servicio LLM."""
    
    def __init__(
        self, 
        detail: str = "Error en el servicio de modelo de lenguaje",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    ):
        super().__init__(status_code, detail)


class ResourceNotFoundException(AppException):
    """Excepción para recursos no encontrados."""
    
    def __init__(
        self, 
        resource_type: str,
        resource_id: str,
        status_code: int = status.HTTP_404_NOT_FOUND
    ):
        detail = f"{resource_type} con ID '{resource_id}' no encontrado"
        super().__init__(status_code, detail)


class InvalidGameStateException(AppException):
    """Excepción para estados inválidos en juegos."""
    
    def __init__(
        self, 
        detail: str = "Estado de juego inválido para esta operación",
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(status_code, detail)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra manejadores de excepciones para la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Manejador para excepciones HTTP estándar."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Manejador para errores de validación de solicitudes."""
        # Log detallado para depuración
        logger.debug(f"Validation error: {exc.errors()}")
        
        # Formatear errores para una respuesta más amigable
        errors = []
        for error in exc.errors():
            loc = ".".join(str(l) for l in error["loc"] if l != "body")
            errors.append({
                "field": loc,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Error de validación en la solicitud",
                "errors": errors
            }
        )
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Manejador para excepciones específicas de la aplicación."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )
    
    @app.exception_handler(LLMServiceException)
    async def llm_exception_handler(request: Request, exc: LLMServiceException) -> JSONResponse:
        """Manejador para excepciones del servicio LLM."""
        logger.error(f"Error en el servicio LLM: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "message": "El servicio de inteligencia artificial está temporalmente no disponible. Por favor, inténtelo de nuevo más tarde."
            }
        )
    
    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
        """Manejador para recursos no encontrados."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Manejador para excepciones no controladas."""
        # Registrar el error para depuración
        logger.exception(f"Error no controlado: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Error interno del servidor",
                "message": "Ha ocurrido un error inesperado. El equipo de desarrollo ha sido notificado."
            }
        )