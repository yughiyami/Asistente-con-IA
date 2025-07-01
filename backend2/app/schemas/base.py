"""
Esquemas base compartidos por toda la aplicación.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Niveles de dificultad para juegos y exámenes"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ResponseStatus(str, Enum):
    """Estados de respuesta estándar"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel):
    """Respuesta base para todas las APIs"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""
    status: ResponseStatus = ResponseStatus.ERROR
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImageData(BaseModel):
    """Datos de imagen generada"""
    url: str
    title: Optional[str] = None
    source: str = "serper"


class Reference(BaseModel):
    """Referencia a fuente académica o documento"""
    title: str
    source: str
    url: Optional[str] = None
    page: Optional[int] = None