"""
Esquemas para el módulo de juegos educativos.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Union, Literal ,Any
from enum import Enum
from .base import DifficultyLevel


class GameType(str, Enum):
    """Tipos de juegos disponibles"""
    HANGMAN = "hangman"
    WORDLE = "wordle"
    LOGIC = "logic"
    ASSEMBLY = "assembly"


class CreateGameRequest(BaseModel):
    """Solicitud para crear un nuevo juego"""
    game_type: GameType = Field(..., description="Tipo de juego a generar")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Nivel de dificultad")
    topic: Optional[str] = Field(None, description="Tema específico para el juego")


# Esquemas para Ahorcado
class HangmanResponse(BaseModel):
    """Respuesta al crear un juego de ahorcado"""
    game_id: str = Field(..., description="Identificador único del juego")
    word_length: int = Field(..., description="Longitud de la palabra a adivinar")
    clue: str = Field(..., description="Pista sobre la palabra")
    argument: str = Field(..., description="Argumento educativo sobre el concepto")
    max_attempts: int = Field(default=6, description="Número máximo de intentos")
    hidden_word: str = Field(..., description="Palabra oculta con guiones bajos")


class HangmanGuessRequest(BaseModel):
    """Solicitud de intento en ahorcado"""
    game_id: str = Field(..., description="Identificador del juego")
    guess: str = Field(..., min_length=1, max_length=20, description="Letra o palabra adivinada")
    
    @validator('guess')
    def validate_guess(cls, v):
        """Valida que el intento sea alfabético"""
        if not v.replace(' ', '').isalpha():
            raise ValueError("El intento debe contener solo letras")
        return v.lower()


class HangmanGuessResponse(BaseModel):
    """Respuesta a un intento de ahorcado"""
    correct: bool = Field(..., description="Si el intento fue correcto")
    current_word: str = Field(..., description="Estado actual de la palabra")
    remaining_attempts: int = Field(..., description="Intentos restantes")
    game_over: bool = Field(..., description="Si el juego terminó")
    win: bool = Field(..., description="Si el jugador ganó")
    correct_word: Optional[str] = Field(None, description="Palabra correcta (solo si game_over)")


# Esquemas para Wordle
class WordleResponse(BaseModel):
    """Respuesta al crear un juego de Wordle"""
    game_id: str = Field(..., description="Identificador único del juego")
    word_length: int = Field(default=5, description="Longitud de la palabra")
    max_attempts: int = Field(default=6, description="Número máximo de intentos")
    topic_hint: str = Field(..., description="Pista temática sobre la palabra")


class WordleGuessRequest(BaseModel):
    """Solicitud de intento en Wordle"""
    game_id: str = Field(..., description="Identificador del juego")
    word: str = Field(..., min_length=5, max_length=5, description="Palabra de 5 letras adivinada")
    
    @validator('word')
    def validate_word(cls, v):
        """Valida que la palabra sea de 5 letras alfabéticas"""
        if not v.isalpha():
            raise ValueError("La palabra debe contener solo letras")
        return v.lower()


class WordleLetterResult(str, Enum):
    """Resultado de cada letra en Wordle"""
    CORRECT = "correct"     # Letra correcta en posición correcta
    PRESENT = "present"     # Letra presente pero en posición incorrecta
    ABSENT = "absent"       # Letra no está en la palabra


class WordleGuessResponse(BaseModel):
    """Respuesta a un intento de Wordle"""
    results: List[WordleLetterResult] = Field(..., min_items=5, max_items=5)
    attempt_number: int = Field(..., description="Número de intento actual")
    remaining_attempts: int = Field(..., description="Intentos restantes")
    game_over: bool = Field(..., description="Si el juego terminó")
    win: bool = Field(..., description="Si el jugador ganó")
    correct_word: Optional[str] = Field(None, description="Palabra correcta (solo si game_over)")
    explanation: Optional[str] = Field(None, description="Explicación del concepto (solo si game_over)")


# Esquemas para Juego de Lógica
# Esquemas mejorados para Juego de Lógica
class LogicGate(BaseModel):
    """Definición de una compuerta lógica"""
    id: str = Field(..., description="ID único de la compuerta")
    type: str = Field(..., description="Tipo: AND, OR, NOT, XOR, NAND, NOR, XNOR")
    inputs: List[str] = Field(..., description="IDs de entradas (pueden ser inputs o otras compuertas)")

class LogicCircuit(BaseModel):
    """Definición del circuito completo"""
    inputs: List[str] = Field(..., description="Nombres de las entradas (A, B, C)")
    gates: List[LogicGate] = Field(..., description="Lista de compuertas")
    output: str = Field(..., description="ID de la compuerta de salida")
    description: str = Field(..., description="Descripción textual del circuito")

class LogicGameResponse(BaseModel):
    """Respuesta al crear un juego de lógica"""
    game_id: str = Field(..., description="Identificador único del juego")
    circuit: LogicCircuit = Field(..., description="Definición del circuito")
    num_inputs: int = Field(..., description="Número de entradas")
    question: str = Field(..., description="Instrucciones para el jugador")

class TruthTableRow(BaseModel):
    """Fila de la tabla de verdad"""
    inputs: Dict[str, int] = Field(..., description="Valores de entrada (ej: {'A': 0, 'B': 1})")
    output: int = Field(..., description="Valor de salida (0 o 1)")

class LogicAnswerRequest(BaseModel):
    """Solicitud de respuesta a juego de lógica"""
    game_id: str = Field(..., description="Identificador del juego")
    truth_table: List[TruthTableRow] = Field(..., description="Tabla de verdad completa")

class LogicAnswerResponse(BaseModel):
    """Respuesta a un intento de juego de lógica"""
    correct: bool = Field(..., description="Si la respuesta fue completamente correcta")
    score: float = Field(..., ge=0, le=100, description="Puntuación obtenida (0-100)")
    explanation: str = Field(..., description="Explicación de la evaluación")
    expected_truth_table: Optional[List[TruthTableRow]] = Field(None, description="Tabla correcta si hubo errores")
# Esquemas para Juego de Ensamblador
class AssemblyGameResponse(BaseModel):
    """Respuesta al crear un juego de ensamblador"""
    game_id: str = Field(..., description="Identificador único del juego")
    code: str = Field(..., description="Código ensamblador con error o para analizar")
    architecture: str = Field(default="x86", description="Arquitectura del procesador")
    expected_behavior: str = Field(..., description="Comportamiento esperado del código")
    hint: str = Field(..., description="Pista para resolver el problema")


class AssemblyAnswerRequest(BaseModel):
    """Solicitud de respuesta a juego de ensamblador"""
    game_id: str = Field(..., description="Identificador del juego")
    explanation: str = Field(..., min_length=10, description="Explicación del error o corrección")


class AssemblyAnswerResponse(BaseModel):
    """Respuesta a un intento de juego de ensamblador"""
    correct: bool = Field(..., description="Si la explicación fue correcta")
    correct_explanation: str = Field(..., description="Explicación correcta del problema")
    score: float = Field(..., ge=0, le=100, description="Puntuación basada en la calidad de la explicación")
    feedback: str = Field(..., description="Retroalimentación específica")