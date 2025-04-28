"""
Dependencias compartidas para los endpoints de la API.
Define funciones para inyección de dependencias en los endpoints.
"""

import logging
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from jose import jwt
from datetime import datetime, timedelta

from app.core.exceptions import ResourceNotFoundException
from app.config import settings
from app.services.llm import llm_service
from app.services.pdf_service import pdf_service
from app.services.games import games_service
from app.repositories.exam_repository import exam_repository

# Configurar logger
logger = logging.getLogger(__name__)

# Esta configuración sería necesaria si implementamos autenticación de usuarios
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/v1/auth/login")


# Dependencias para servicios

def get_llm_service():
    """
    Proporciona una instancia del servicio LLM.
    
    Returns:
        Instancia configurada del servicio LLM
    """
    return llm_service


def get_pdf_service():
    """
    Proporciona una instancia del servicio de PDFs.
    
    Returns:
        Instancia configurada del servicio de PDFs
    """
    return pdf_service


def get_games_service():
    """
    Proporciona una instancia del servicio de juegos.
    
    Returns:
        Instancia configurada del servicio de juegos
    """
    return games_service


def get_exam_repository():
    """
    Proporciona una instancia del repositorio de exámenes.
    
    Returns:
        Instancia configurada del repositorio de exámenes
    """
    return exam_repository


# Estas dependencias serían necesarias si implementamos autenticación de usuarios

# def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
#     """
#     Verifica un token JWT y devuelve los datos del usuario.
#     
#     Args:
#         token: Token JWT a verificar
#         
#     Returns:
#         Datos del usuario extraídos del token
#         
#     Raises:
#         HTTPException: Si el token es inválido o ha expirado
#     """
#     try:
#         # Decodificar token
#         payload = jwt.decode(
#             token, 
#             settings.SECRET_KEY, 
#             algorithms=["HS256"]
#         )
#         
#         # Verificar expiración
#         expiration = datetime.fromtimestamp(payload.get("exp", 0))
#         if datetime.now() > expiration:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Token expirado",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         
#         return payload
#         
#     except (jwt.JWTError, ValidationError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Credenciales inválidas",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
# 
# 
# def get_current_user(token_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
#     """
#     Obtiene los datos del usuario autenticado.
#     
#     Args:
#         token_data: Datos del token verificado
#         
#     Returns:
#         Datos del usuario autenticado
#     """
#     # En una implementación real, aquí se consultaría la base de datos
#     user_id = token_data.get("sub")
#     
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Usuario no identificado",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     
#     # Devolver datos del usuario (simulados)
#     return {
#         "id": user_id,
#         "email": token_data.get("email", ""),
#         "role": token_data.get("role", "student")
#     }