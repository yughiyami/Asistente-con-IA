"""
Aplicación principal FastAPI.
Configura la aplicación, middleware, routers y manejo de errores.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from contextlib import asynccontextmanager
from typing import Dict

from app.core.config import settings
from app.core.dependencies import cleanup_services, check_services_health
from app.api.v1 import chat, exam, games
from app.schemas.base import ErrorResponse, ResponseStatus

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    Inicialización y limpieza de recursos.
    """
    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    
    # Verificar salud de servicios
    health = await check_services_health()
    logger.info(f"Estado de servicios: {health}")
    
    if not health["redis"]:
        logger.warning("Redis no está disponible. Algunas funciones pueden estar limitadas.")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    cleanup_services()
    logger.info("Aplicación cerrada correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para el Asistente de Aprendizaje de Arquitectura de Computadoras",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat.router)
app.include_router(exam.router)
app.include_router(games.router)


# Manejadores de excepciones globales
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Maneja errores de validación de Pydantic.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    error_response = ErrorResponse(
        status=ResponseStatus.ERROR,
        message="Error de validación en los datos enviados",
        detail="; ".join(errors)
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error_response.dict())  # ← AGREGAR jsonable_encoder
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Maneja excepciones HTTP generales.
    """
    error_response = ErrorResponse(
        status=ResponseStatus.ERROR,
        message=exc.detail,
        detail=None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response.dict())  # ← AGREGAR jsonable_encoder
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Maneja excepciones no capturadas.
    """
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        status=ResponseStatus.ERROR,
        message="Error interno del servidor",
        detail=str(exc) if settings.debug else None
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(error_response.dict())  # ← AGREGAR jsonable_encoder
    )


# Endpoints de utilidad
@app.get("/")
async def root():
    """
    Endpoint raíz con información básica de la API.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud.
    Útil para monitoreo y balanceadores de carga.
    """
    health_status = await check_services_health()
    
    # Determinar estado general
    all_healthy = all(health_status.values())
    critical_services = ["gemini", "redis"]
    critical_healthy = all(health_status[service] for service in critical_services)
    
    if all_healthy:
        status_code = status.HTTP_200_OK
        overall_status = "healthy"
    elif critical_healthy:
        status_code = status.HTTP_200_OK
        overall_status = "degraded"
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = "unhealthy"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "version": settings.app_version,
            "services": health_status
        }
    )


@app.get("/api/v1/info")
async def api_info():
    """
    Información detallada sobre la API.
    """
    return {
        "version": "1.0.0",
        "endpoints": {
            "chat": {
                "description": "Interfaz de chat con IA para consultas educativas",
                "methods": ["POST /api/v1/chat/", "GET /api/v1/chat/documents"]
            },
            "exam": {
                "description": "Generación y validación de exámenes",
                "methods": ["POST /api/v1/exam/generate", "POST /api/v1/exam/validate"]
            },
            "games": {
                "description": "Juegos educativos interactivos",
                "types": ["hangman", "wordle", "logic", "assembly"],
                "methods": [
                    "POST /api/v1/games/",
                    "POST /api/v1/games/{type}",
                    "POST /api/v1/games/{type}/guess",
                    "POST /api/v1/games/{type}/answer"
                ]
            }
        },
        "features": [
            "Chat con contexto de documentos PDF",
            "Generación de imágenes educativas",
            "Exámenes personalizados con retroalimentación",
            "Juegos interactivos para aprendizaje",
            "Persistencia de sesiones con Redis"
        ]
    }


# Middleware personalizado para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Registra todas las peticiones HTTP.
    """
    # Excluir health checks del logging detallado
    if request.url.path not in ["/health", "/"]:
        logger.info(f"{request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log de errores
    if response.status_code >= 400:
        logger.warning(
            f"{request.method} {request.url.path} - Status: {response.status_code}"
        )
    
    return response