"""
Configuración central de la aplicación.
Maneja variables de entorno y configuraciones globales.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """configuración de la aplicación.      """
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # App info
    app_name: str = "Asistente de Arquitectura de Computadoras"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Keys
    gemini_api_key: str
    serper_api_key: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    # Session
    session_expire_minutes: int = 60
    
    # Límites de juego
    max_hangman_attempts: int = 6
    max_wordle_attempts: int = 6
    wordle_word_length: int = 5
    
    # Límites de examen
    max_exam_questions: int = 10
    default_exam_questions: int = 5
    exam_time_limit_easy: int = 20
    exam_time_limit_medium: int = 30
    exam_time_limit_hard: int = 45
    
    class Config:
        env_file = ".env"
        case_sensitive = False
@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración cacheada de la aplicación.
    Usa lru_cache para evitar recrear el objeto en cada llamada.
    """
    return Settings()


# Instancia global de configuración
settings = get_settings()