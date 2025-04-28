"""
Configuración centralizada para la aplicación.
Utiliza Pydantic para validar las variables de entorno y proporcionar valores por defecto.
"""

import secrets
from typing import List, Optional, Union, Dict, Any
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuración de la aplicación utilizando variables de entorno.
    
    Attributes:
        API_PREFIX: Prefijo para todas las rutas de la API
        PROJECT_NAME: Nombre del proyecto
        SECRET_KEY: Clave secreta para tokens y operaciones de seguridad
        GEMINI_API_KEY: Clave de API para el servicio GEMINI
        CORS_ORIGINS: Lista de orígenes permitidos para CORS
        PDF_LIBRARY_PATH: Ruta a la biblioteca de PDFs del curso
        MONGODB_URI: URI de conexión a MongoDB (opcional)
    """
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Asistente de Arquitectura de Computadoras"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    GEMINI_API_KEY: str
    SERPER_API_KEY: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    # Configuración CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    SYSTEM_PROMPT: str = """
    Eres un asistente educativo especializado en Arquitectura de Computadoras. Tu objetivo es ayudar a los estudiantes
    a comprender conceptos de arquitectura de computadoras, responder preguntas tecnicas, generar exmenes relevantes y
    ofrecer juegos educativos. Utiliza un lenguaje claro y preciso. Basas tus respuestas en libros academicos de la materia.
    """

    # Configuración del modelo
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_P: float = 0.8
    LLM_TOP_K: int = 40
    LLM_MAX_OUTPUT_TOKENS: int = 1024

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Valida y formatea los orígenes CORS desde variables de entorno."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Rutas para recursos
    PDF_LIBRARY_PATH: str = "static/pdf_library"
    
    # Base de datos (opcional, dependiendo de la implementación)
    MONGODB_URI: Optional[str] = None
    MONGODB_DB_NAME: Optional[str] = "architecture_assistant"
        # Configuración de imágenes
    MAX_IMAGES_PER_RESPONSE: int = 3


    # Configuración específica para juegos
    GAMES_CONFIG: Dict[str, Any] = {
        "hangman": {
            "word_list": [
                "PROCESADOR", "MEMORIA", "CACHE", "REGISTRO", "PIPELINE", 
                "ARQUITECTURA", "ENSAMBLADOR", "INTERRUPCIONES", "DIRECCIONAMIENTO",
                "MICROPROCESADOR", "FIRMWARE", "MICROCONTROLADOR", "BUSES", "ALU",
                "RISC", "CISC", "CPU", "GPU", "SUPERESCALAR", "PIPELINING"
            ],
            "max_attempts": 6
        },
        "wordle": {
            "word_list": ["CACHE", "STACK", "BUSES", "CLOCK", "RISC", "CISC", "FETCH", 
                         "STORE", "PORTS", "QUEUE"],
            "max_attempts": 6
        }
    }
    class Config:
        """Configuración para cargar variables desde archivo .env"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia de configuración global
settings = Settings()