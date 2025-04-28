"""
Router principal que agrupa todos los endpoints de la API.
Organiza las rutas por versión y funcionalidad.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, exam, games

# Router principal para todas las rutas de la API
api_router = APIRouter()

# Registrar routers de la v1 de la API
api_router.include_router(
    chat.router,
    prefix="/v1/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    exam.router,
    prefix="/v1/exam",
    tags=["exam"],
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    games.router,
    prefix="/v1/games",
    tags=["games"],
    responses={404: {"description": "Not found"}},
)

# Aquí se pueden agregar más routers para futuras versiones o funcionalidades