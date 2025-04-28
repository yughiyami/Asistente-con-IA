"""
Punto de entrada principal para la aplicación FastAPI del Asistente de Arquitectura de Computadoras.
Este archivo configura la aplicación FastAPI, registra los routers y middleware necesarios.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.exceptions import register_exception_handlers
from app.config import settings

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para el Asistente de Aprendizaje de Arquitectura de Computadoras",
    version="1.0.0",
    docs_url=None,  # Desactivamos los docs por defecto para personalizarlos
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores de excepciones
register_exception_handlers(app)

# Incluir router principal
app.include_router(api_router, prefix=settings.API_PREFIX)

# Montar carpeta de archivos estáticos (si es necesario)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Personalizar la página de documentación Swagger
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Personaliza la interfaz de Swagger UI."""
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/", include_in_schema=False)
async def root():
    """Ruta raíz con información básica de la API."""
    return {
        "message": "¡Bienvenido al Asistente de Arquitectura de Computadoras!",
        "version": "1.0.0",
        "documentation": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)