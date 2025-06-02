"""
Esquemas Pydantic para las solicitudes y respuestas del modo Juegos.
Define la estructura para los diferentes juegos educativos disponibles.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class GameType(str, Enum):
    """Tipos de juegos disponibles en el sistema."""
    HANGMAN = "hangman"  # Ahorcado
    WORDLE = "wordle"    # Wordle de términos técnicos
    LOGIC = "logic"      # Diagrama lógico
    ASSEMBLY = "assembly"  # Juego de ensamblador


class DifficultyLevel(str, Enum):
    """Niveles de dificultad disponibles para los juegos."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GameRequest(BaseModel):
    """
    Solicitud para generar un juego - SIN CAMBIOS.
    """
    game_type: GameType = Field(..., 
                               description="Tipo de juego a generar")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM,
                                      description="Nivel de dificultad")
    topic: Optional[str] = Field(default=None,
                               description="Tema específico para el juego",
                               example="procesador")


# Esquemas para el juego de Ahorcado (Hangman) - SIN CAMBIOS MAYORES

class HangmanResponse(BaseModel):
    """Respuesta para el juego de Ahorcado - Limitado a 100 palabras en campos de texto."""
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    word_length: int = Field(..., 
                           description="Longitud de la palabra a adivinar")
    clue: str = Field(..., 
                     description="Pista sobre la palabra (máximo 100 caracteres)",
                     max_length=100,
                     example="Componente que almacena temporalmente datos")
    argument: str = Field(..., 
                         description="Explicación educativa sobre el término (máximo 100 caracteres)",
                         max_length=100,
                         example="Fundamental en arquitectura por su velocidad de acceso")
    max_attempts: int = Field(default=6,
                            description="Número máximo de intentos permitidos")
    hidden_word: str = Field(..., 
                            description="Representación inicial de la palabra oculta",
                            example="_ _ _ _ _ _")


class HangmanGuessRequest(BaseModel):
    """Solicitud para adivinar una letra o palabra en el juego de Ahorcado - SIN CAMBIOS."""
    game_id: str = Field(..., 
                         description="Identificador del juego")
    guess: str = Field(..., 
                       description="Letra o palabra adivinada",
                       example="a")


class HangmanGuessResponse(BaseModel):
    """Respuesta a un intento de adivinanza en el juego de Ahorcado - SIN CAMBIOS."""
    correct: bool = Field(..., 
                         description="Si la letra/palabra es correcta")
    current_word: str = Field(..., 
                             description="Estado actual de la palabra con las letras adivinadas",
                             example="_ a _ _ _ _")
    remaining_attempts: int = Field(..., 
                                  description="Intentos restantes")
    game_over: bool = Field(..., 
                           description="Si el juego ha terminado")
    win: Optional[bool] = Field(default=None,
                              description="Si el jugador ha ganado (solo cuando game_over=True)")
    correct_word: Optional[str] = Field(default=None,
                                     description="Palabra correcta (solo cuando game_over=True)")


# Esquemas para el juego de Wordle - LIMITADO A 100 PALABRAS

class WordleResponse(BaseModel):
    """Respuesta para el juego de Wordle - Limitado a 100 palabras en campos de texto."""
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    word_length: int = Field(default=5,
                           description="Longitud de la palabra (siempre 5)")
    max_attempts: int = Field(default=6,
                            description="Número máximo de intentos permitidos")
    topic_hint: str = Field(..., 
                           description="Pista sobre el tema de la palabra (máximo 100 caracteres)",
                           max_length=100,
                           example="Relacionado con almacenamiento de datos")


class WordleGuessRequest(BaseModel):
    """Solicitud para adivinar una palabra en el juego de Wordle - SIN CAMBIOS."""
    game_id: str = Field(..., 
                         description="Identificador del juego")
    word: str = Field(..., 
                      description="Palabra de 5 letras adivinada",
                      min_length=5, max_length=5,
                      example="cache")


class LetterResult(str, Enum):
    """Resultado de cada letra en Wordle - SIN CAMBIOS."""
    CORRECT = "correct"  # Letra correcta en posición correcta
    PRESENT = "present"  # Letra correcta en posición incorrecta
    ABSENT = "absent"    # Letra no presente en la palabra


class WordleGuessResponse(BaseModel):
    """Respuesta a un intento de adivinanza en el juego de Wordle - Limitado a 100 palabras."""
    results: List[LetterResult] = Field(..., 
                                      description="Resultados para cada letra",
                                      example=["correct", "absent", "present", "absent", "correct"])
    attempt_number: int = Field(..., 
                              description="Número de intento actual")
    remaining_attempts: int = Field(..., 
                                  description="Intentos restantes")
    game_over: bool = Field(..., 
                           description="Si el juego ha terminado")
    win: Optional[bool] = Field(default=None,
                              description="Si el jugador ha ganado (solo cuando game_over=True)")
    correct_word: Optional[str] = Field(default=None,
                                     description="Palabra correcta (solo cuando game_over=True)")
    explanation: Optional[str] = Field(default=None,
                                    description="Explicación del término cuando el juego termina (máximo 400 caracteres)",
                                    max_length=400,
                                    example="Cache: componente que almacena datos para acceso rápido.")


# Esquemas para el juego de Diagrama Lógico - COMPLETAMENTE REDISEÑADO

class LogicResponse(BaseModel):
    """
    Respuesta para el juego de Diagrama Lógico - CON COMPLEJIDAD VARIABLE.
    
    Attributes:
        game_id: Identificador único del juego
        difficulty: Nivel de dificultad del juego
        pattern: Lista de compuertas en orden de ejecución
        question: Pregunta sobre el circuito
        input_values: Matriz de entradas y salidas por compuerta en orden
        expected_output: Salida esperada (simple para easy, compleja para medium/hard)
        complexity_type: Tipo de complejidad según dificultad
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    difficulty: str = Field(...,
                          description="Nivel de dificultad del juego",
                          example="medium")
    pattern: List[str] = Field(..., 
                              description="Lista de compuertas en orden de ejecución",
                              example=["AND", "OR", "XOR"])
    question: str = Field(..., 
                         description="Pregunta sobre el circuito",
                         example="¿Cuáles son las salidas para los casos de prueba?")
    input_values: List[List[int]] = Field(..., 
                                         description="Matriz de entradas y salidas por compuerta en orden",
                                         example=[[1, 1, 1], [1, 0, 1], [1, 1, 0]])
    expected_output: Union[int, List[int], Dict[str, Union[int, List[int]]]] = Field(..., 
                                description="Salida esperada (varía según dificultad)",
                                example={"case1": 0, "case2": 1, "pattern": [0, 1, 0, 1]})
    complexity_type: str = Field(...,
                                description="Tipo de complejidad",
                                example="multiple_cases")


class LogicAnswerRequest(BaseModel):
    """
    Solicitud para responder al juego de Diagrama Lógico - CON COMPLEJIDAD VARIABLE.
    
    Attributes:
        game_id: Identificador del juego
        answer: Respuesta del usuario (varía según dificultad)
    """
    game_id: str = Field(..., 
                         description="Identificador del juego")
    answer: Union[int, List[int], Dict[str, Union[int, List[int]]]] = Field(..., 
                       description="Respuesta del usuario (varía según dificultad)",
                       example={"case1": 0, "case2": 1, "pattern": [0, 1, 0, 1]})


class LogicAnswerResponse(BaseModel):
    """
    Respuesta a la solución propuesta para el juego de Diagrama Lógico - CON COMPLEJIDAD VARIABLE.
    """
    correct: bool = Field(..., 
                         description="Si la respuesta es correcta")
    correct_answer: Union[int, List[int], Dict[str, Union[int, List[int]]]] = Field(..., 
                               description="Respuesta correcta")
    partial_score: Optional[float] = Field(default=None,
                                         description="Puntuación parcial para respuestas complejas")
    explanation: str = Field(..., 
                            description="Explicación del funcionamiento del circuito (máximo 400 caracteres)",
                            max_length=400,
                            example="Caso 1: AND(1,1)=1, OR(1,0)=1, XOR(1,1)=0. Caso 2: AND(0,1)=0, OR(0,1)=1, XOR(1,1)=0.")
    complexity_feedback: Optional[str] = Field(default=None,
                                             description="Retroalimentación específica sobre la complejidad")

# Esquemas para el juego de Ensamblador - COMPLETAMENTE REDISEÑADO

class AssemblyResponse(BaseModel):
    """
    Respuesta para el juego de Ensamblador - Limitado a 100 palabras en campos de texto.
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    code: str = Field(..., 
                     description="Código en ensamblador con errores",
                     example="MOV AX, 5\nADD AX, 10\nMOV BX, AX\nSUB AX, BX")
    architecture: str = Field(..., 
                            description="Arquitectura del ensamblador",
                            example="x86")
    expected_behavior: str = Field(..., 
                                 description="Comportamiento esperado del código (máximo 100 caracteres)",
                                 max_length=100,
                                 example="El programa debe calcular AX = 0")
    hint: str = Field(..., 
                     description="Pista sobre el error (máximo 100 caracteres)",
                     max_length=100,
                     example="Revisa la instrucción SUB y sus operandos")


class AssemblyAnswerRequest(BaseModel):
    """
    Solicitud para responder al juego de Ensamblador - REDISEÑADO: SOLO EXPLICACIÓN.
    
    Attributes:
        game_id: Identificador del juego
        explanation: Explicación del error o código correcto con palabras del usuario
    """
    game_id: str = Field(..., 
                         description="Identificador del juego")
    explanation: str = Field(..., 
                           description="Explicación del error encontrado en el código o descripción de la corrección",
                           min_length=10,
                           example="El error está en la instrucción SUB AX, BX porque debería ser SUB AX, AX para obtener 0, ya que cualquier número menos sí mismo es 0.")


class AssemblyAnswerResponse(BaseModel):
    """
    Respuesta a la solución propuesta para el juego de Ensamblador - Limitado a 100 palabras.
    """
    correct: bool = Field(..., 
                         description="Si la explicación es correcta")
    explanation: str = Field(..., 
                            description="Retroalimentación sobre la explicación (máximo 400 caracteres)",
                            max_length=400,
                            example="¡Correcto! Identificaste que SUB AX, BX era incorrecto. La solución SUB AX, AX es perfecta.")
    correct_solution: Optional[str] = Field(default=None,
                                         description="Solución correcta cuando la explicación es incorrecta (máximo 100 caracteres)",
                                         max_length=100)