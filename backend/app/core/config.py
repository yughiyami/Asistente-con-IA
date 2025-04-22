import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Asistente de Arquitectura de Computadoras"
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/computer_arch_assistant")
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # API de búsqueda de imágenes (puedes usar Serper, SerpAPI, etc.)
    IMAGE_SEARCH_API_KEY: str = os.getenv("IMAGE_SEARCH_API_KEY")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend dev
        "http://localhost:8000",  # Backend dev
        "http://192.168.56.1:3000"
        "https://asistente-arquitectura.vercel.app"  # Producción
    ]
    
    # Configuraciones de los juegos
    GAMES_CONFIG: dict = {
        "hangman": {
            "word_list": ["PROCESADOR", "MEMORIA", "REGISTRO", "CACHE", "PIPELINE", 
                         "ARQUITECTURA", "ENSAMBLADOR", "INTERRUPCIONES", "DIRECCIONAMIENTO", 
                         "MICROPROCESADOR", "FIRMWARE", "MICROCONTROLADOR"]
        }
    }
    
    # Rutas a los archivos de contenido
    CONTENT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    
    # Prompts del sistema
    SYSTEM_PROMPT: str = """
    Eres un asistente educativo especializado en Arquitectura de Computadoras. Tu objetivo es ayudar a los estudiantes
    a comprender conceptos de arquitectura de computadoras, responder preguntas tecnicas, generar exmenes relevantes y
    ofrecer juegos educativos. Utiliza un lenguaje claro y preciso. Basas tus respuestas en libros academicos de la materia.
    """

settings = Settings()