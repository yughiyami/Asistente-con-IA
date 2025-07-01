"""
Router para endpoints de juegos educativos.
Maneja todos los tipos de juegos: ahorcado, wordle, lógica y ensamblador.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Union
import logging

from app.schemas.games import (
    GameType, CreateGameRequest,
    HangmanResponse, HangmanGuessRequest, HangmanGuessResponse,
    WordleResponse, WordleGuessRequest, WordleGuessResponse,
    LogicGameResponse, LogicAnswerRequest, LogicAnswerResponse,  # Agregar aquí
    AssemblyGameResponse, AssemblyAnswerRequest, AssemblyAnswerResponse
)
from app.services.game_service import GameService
from app.services.gemini_service import GeminiService
from app.services.redis_service import RedisService
from app.core.dependencies import get_game_service , get_gemini_service, get_redis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/games", tags=["games"])


@router.post("/", response_model=Union[HangmanResponse, WordleResponse, LogicGameResponse, AssemblyGameResponse])
async def create_game(
    request: CreateGameRequest,
    game_service: GameService = Depends(get_game_service)
):
    """
    Crea un nuevo juego del tipo especificado.
    
    Tipos disponibles:
    - hangman: Juego del ahorcado con términos de arquitectura
    - wordle: Wordle con palabras de 5 letras relacionadas
    - logic: Juego de compuertas lógicas
    - assembly: Análisis de código ensamblador
    """
    try:
        if request.game_type == GameType.HANGMAN:
            return await game_service.create_hangman_game(
                topic=request.topic,
                difficulty=request.difficulty
            )
        elif request.game_type == GameType.WORDLE:
            return await game_service.create_wordle_game(
                topic=request.topic,
                difficulty=request.difficulty
            )
        elif request.game_type == GameType.LOGIC:
            return await game_service.create_logic_game(
                difficulty=request.difficulty
            )
        elif request.game_type == GameType.ASSEMBLY:
            return await game_service.create_assembly_game(
                difficulty=request.difficulty
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de juego no soportado: {request.game_type}"
            )
            
    except Exception as e:
        logger.error(f"Error creando juego {request.game_type}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el juego: {str(e)}"
        )


# Endpoints específicos para Ahorcado
@router.post("/hangman", response_model=HangmanResponse)
async def create_hangman_game(
    request: CreateGameRequest,
    game_service: GameService = Depends(get_game_service)
) -> HangmanResponse:
    """
    Crea un nuevo juego de ahorcado.
    
    - Genera una palabra relacionada con arquitectura de computadoras
    - Proporciona una pista y argumento educativo
    - Dificultad afecta la longitud y complejidad de la palabra
    """
    try:
        return await game_service.create_hangman_game(
            topic=request.topic,
            difficulty=request.difficulty
        )
    except Exception as e:
        logger.error(f"Error creando juego de ahorcado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el juego: {str(e)}"
        )


@router.post("/hangman/guess", response_model=HangmanGuessResponse)
async def guess_hangman(
    request: HangmanGuessRequest,
    game_service: GameService = Depends(get_game_service)
) -> HangmanGuessResponse:
    """
    Procesa un intento en el juego de ahorcado.
    
    - Acepta letras individuales o palabras completas
    - Actualiza el estado del juego
    - Retorna si el intento fue correcto y el estado actual
    """
    try:
        return await game_service.guess_hangman(
            game_id=request.game_id,
            guess=request.guess
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error procesando intento de ahorcado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el intento: {str(e)}"
        )


# Endpoints específicos para Wordle
@router.post("/wordle", response_model=WordleResponse)
async def create_wordle_game(
    request: CreateGameRequest,
    game_service: GameService = Depends(get_game_service)
) -> WordleResponse:
    """
    Crea un nuevo juego de Wordle.
    
    - Genera una palabra de 5 letras relacionada con el tema
    - Proporciona una pista temática sin revelar la palabra
    - Máximo 6 intentos para adivinar
    """
    try:
        return await game_service.create_wordle_game(
            topic=request.topic,
            difficulty=request.difficulty
        )
    except Exception as e:
        logger.error(f"Error creando juego de Wordle: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el juego: {str(e)}"
        )


@router.post("/wordle/guess", response_model=WordleGuessResponse)
async def guess_wordle(
    request: WordleGuessRequest,
    game_service: GameService = Depends(get_game_service)
) -> WordleGuessResponse:
    """
    Procesa un intento en el juego de Wordle.
    
    - Evalúa cada letra: correcta, presente o ausente
    - Actualiza el contador de intentos
    - Al finalizar, proporciona explicación del concepto
    """
    try:
        return await game_service.guess_wordle(
            game_id=request.game_id,
            word=request.word
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error procesando intento de Wordle: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el intento: {str(e)}"
        )


# Endpoints específicos para Juego de Lógica
@router.post("/logic", response_model=LogicGameResponse)
async def create_logic_game(
    request: CreateGameRequest,
    game_service: GameService = Depends(get_game_service)
) -> LogicGameResponse:
    """
    Crea un nuevo juego de Compuertas Lógicas.
    
    Niveles de dificultad:
    - easy: Una salida simple
    - medium: Múltiples casos de prueba
    - hard: Reconocimiento de patrones
    """
    try:
        return await game_service.create_logic_game(
            difficulty=request.difficulty
        )
    except Exception as e:
        logger.error(f"Error creando juego de lógica: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el juego: {str(e)}"
        )


@router.post("/logic/answer", response_model=LogicAnswerResponse)
async def answer_logic(
    request: LogicAnswerRequest,
    game_service: GameService = Depends(get_game_service)
) -> LogicAnswerResponse:
    """
    Procesa la respuesta a un juego de Compuertas Lógicas.
    
    - Evalúa la respuesta según el tipo de complejidad
    - Proporciona puntuación parcial cuando aplica
    - Incluye explicación detallada de la solución
    """
    try:
        return await game_service.answer_logic(
            game_id=request.game_id,
            truth_table=request.truth_table
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error procesando respuesta de lógica: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la respuesta: {str(e)}"
        )


# Endpoints específicos para Juego de Ensamblador
@router.post("/assembly", response_model=AssemblyGameResponse)
async def create_assembly_game(
    request: CreateGameRequest,
    game_service: GameService = Depends(get_game_service)
) -> AssemblyGameResponse:
    """
    Crea un nuevo juego de análisis de código ensamblador.
    
    - Presenta código x86 con errores o para analizar
    - El estudiante debe identificar y explicar el problema
    - Enfocado en conceptos educativos de arquitectura
    """
    try:
        return await game_service.create_assembly_game(
            difficulty=request.difficulty
        )
    except Exception as e:
        logger.error(f"Error creando juego de ensamblador: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el juego: {str(e)}"
        )


@router.post("/assembly/answer", response_model=AssemblyAnswerResponse)
async def answer_assembly(
    request: AssemblyAnswerRequest,
    game_service: GameService = Depends(get_game_service)
) -> AssemblyAnswerResponse:
    """
    Procesa la respuesta a un juego de ensamblador.
    
    - Evalúa la explicación del estudiante
    - Proporciona puntuación basada en precisión
    - Incluye retroalimentación educativa específica
    """
    try:
        return await game_service.answer_assembly(
            game_id=request.game_id,
            explanation=request.explanation
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error procesando respuesta de ensamblador: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la respuesta: {str(e)}"
        )


# Endpoint de utilidad para obtener estado de juego
@router.get("/status/{game_type}/{game_id}")
async def get_game_status(
    game_type: GameType,
    game_id: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Obtiene el estado actual de un juego.
    
    Útil para:
    - Recuperar juegos en progreso
    - Verificar si un juego existe
    - Debugging
    """
    try:
        game_state = await redis_service.get_game_state(game_id, game_type.value)
        
        if not game_state:
            raise HTTPException(
                status_code=404,
                detail="Juego no encontrado"
            )
        
        # Filtrar información sensible según el tipo de juego
        if game_type in [GameType.HANGMAN, GameType.WORDLE] and not game_state.get("game_over", False):
            # No revelar la palabra si el juego no ha terminado
            game_state.pop("word", None)
        
        return game_state
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado del juego: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el estado: {str(e)}"
        )