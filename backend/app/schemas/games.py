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
    Solicitud para generar un juego.
    
    Attributes:
        game_type: Tipo de juego solicitado
        difficulty: Nivel de dificultad
        topic: Tema específico (opcional)
    """
    game_type: GameType = Field(..., 
                               description="Tipo de juego a generar")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM,
                                      description="Nivel de dificultad")
    topic: Optional[str] = Field(default=None,
                               description="Tema específico para el juego",
                               example="Memoria caché")


# Esquemas para el juego de Ahorcado (Hangman)

class HangmanResponse(BaseModel):
    """
    Respuesta para el juego de Ahorcado.
    
    Attributes:
        game_id: Identificador único del juego
        word_length: Longitud de la palabra a adivinar
        clue: Pista sobre la palabra
        argument: Explicación educativa sobre el término
        max_attempts: Número máximo de intentos permitidos
        hidden_word: Representación inicial de la palabra oculta
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    word_length: int = Field(..., 
                           description="Longitud de la palabra a adivinar")
    clue: str = Field(..., 
                     description="Pista sobre la palabra",
                     example="Componente que almacena temporalmente datos e instrucciones")
    argument: str = Field(..., 
                         description="Explicación educativa sobre el término",
                         example="Este componente es fundamental en la arquitectura de computadoras debido a su velocidad de acceso...")
    max_attempts: int = Field(default=6,
                            description="Número máximo de intentos permitidos")
    hidden_word: str = Field(..., 
                            description="Representación inicial de la palabra oculta",
                            example="_ _ _ _ _ _")


class HangmanGuessRequest(BaseModel):
    """
    Solicitud para adivinar una letra o palabra en el juego de Ahorcado.
    
    Attributes:
        game_id: Identificador del juego
        guess: Letra o palabra adivinada
    """
    game_id: str = Field(..., 
                         description="Identificador del juego")
    guess: str = Field(..., 
                       description="Letra o palabra adivinada",
                       example="a")


class HangmanGuessResponse(BaseModel):
    """
    Respuesta a un intento de adivinanza en el juego de Ahorcado.
    
    Attributes:
        correct: Si la letra/palabra es correcta
        current_word: Estado actual de la palabra con las letras adivinadas
        remaining_attempts: Intentos restantes
        game_over: Si el juego ha terminado
        win: Si el jugador ha ganado (solo cuando game_over=True)
        correct_word: Palabra correcta (solo cuando game_over=True)
    """
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


# Esquemas para el juego de Wordle

class WordleResponse(BaseModel):
    """
    Respuesta para el juego de Wordle.
    
    Attributes:
        game_id: Identificador único del juego
        word_length: Longitud de la palabra (siempre 5)
        max_attempts: Número máximo de intentos permitidos
        topic_hint: Pista sobre el tema de la palabra
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    word_length: int = Field(default=5,
                           description="Longitud de la palabra (siempre 5)")
    max_attempts: int = Field(default=6,
                            description="Número máximo de intentos permitidos")
    topic_hint: str = Field(..., 
                           description="Pista sobre el tema de la palabra",
                           example="Relacionado con almacenamiento de datos")


class WordleGuessRequest(BaseModel):
    """
    Solicitud para adivinar una palabra en el juego de Wordle.
    
    Attributes:
        game_id: Identificador del juego
        word: Palabra de 5 letras adivinada
    """
    game_id: str = Field(..., 
                         description="Identificador del juego")
    word: str = Field(..., 
                      description="Palabra de 5 letras adivinada",
                      min_length=5, max_length=5,
                      example="cache")


class LetterResult(str, Enum):
    """Resultado de cada letra en Wordle."""
    CORRECT = "correct"  # Letra correcta en posición correcta
    PRESENT = "present"  # Letra correcta en posición incorrecta
    ABSENT = "absent"    # Letra no presente en la palabra


class WordleGuessResponse(BaseModel):
    """
    Respuesta a un intento de adivinanza en el juego de Wordle.
    
    Attributes:
        results: Lista de resultados para cada letra
        attempt_number: Número de intento actual
        remaining_attempts: Intentos restantes
        game_over: Si el juego ha terminado
        win: Si el jugador ha ganado (solo cuando game_over=True)
        correct_word: Palabra correcta (solo cuando game_over=True)
    """
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
                                    description="Explicación del término cuando el juego termina",
                                    example="Cache es un componente de hardware o software que almacena datos para que futuras solicitudes de esos datos puedan ser atendidas más rápidamente.")


# Esquemas para el juego de Diagrama Lógico

class LogicResponse(BaseModel):
    """
    Respuesta para el juego de Diagrama Lógico.
    
    Attributes:
        game_id: Identificador único del juego
        pattern: Descripción del patrón lógico
        question: Pregunta sobre el patrón
        input_values: Lista de valores de entrada de ejemplo
        expected_output: Lista de valores de salida esperados
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    pattern: str = Field(..., 
                        description="Descripción del patrón lógico",
                        example="Compuerta AND con tres entradas")
    question: str = Field(..., 
                         description="Pregunta sobre el patrón",
                         example="¿Cuál sería la salida si las entradas son 1, 0, 1?")
    input_values: List[List[Union[int, str]]] = Field(..., 
                                              description="Lista de valores de entrada de ejemplo",
                                              example=[[1, 1, 1], [1, 0, 1], [0, 1, 1]])
    expected_output: List[Union[int, str]] = Field(..., 
                                           description="Lista de valores de salida esperados",
                                           example=[1, 0, 0])


class LogicAnswerRequest(BaseModel):
    """
    Solicitud para responder al juego de Diagrama Lógico.
    
    Attributes:
        game_id: Identificador del juego
        answers: Lista de respuestas para cada entrada
    """
    game_id: str = Field(..., 
                         description="Identificador del juego")
    answers: List[Union[int, str]] = Field(..., 
                                   description="Lista de respuestas para cada entrada",
                                   example=[1, 0, 0])


class LogicAnswerResponse(BaseModel):
    """
    Respuesta a la solución propuesta para el juego de Diagrama Lógico.
    
    Attributes:
        correct: Si todas las respuestas son correctas
        correct_answers: Lista de respuestas correctas
        explanation: Explicación de la lógica del patrón
    """
    correct: bool = Field(..., 
                         description="Si todas las respuestas son correctas")
    correct_answers: List[Union[int, str]] = Field(..., 
                                           description="Lista de respuestas correctas")
    explanation: str = Field(..., 
                            description="Explicación de la lógica del patrón",
                            example="Una compuerta AND de tres entradas produce un 1 en la salida solo cuando todas las entradas son 1, en cualquier otro caso produce un 0.")


# Esquemas para el juego de Ensamblador

class AssemblyResponse(BaseModel):
    """
    Respuesta para el juego de Ensamblador.
    
    Attributes:
        game_id: Identificador único del juego
        code: Código en ensamblador con errores
        architecture: Arquitectura del ensamblador (MIPS, x86, etc.)
        expected_behavior: Comportamiento esperado del código
        hint: Pista sobre el error
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del juego")
    code: str = Field(..., 
                     description="Código en ensamblador con errores",
                     example="MOV AX, 5\nADD AX, 10\nMOV BX, AX\nSUB AX, BX\n; El resultado debería ser 0")
    architecture: str = Field(..., 
                            description="Arquitectura del ensamblador",
                            example="x86")
    expected_behavior: str = Field(..., 
                                 description="Comportamiento esperado del código",
                                 example="El programa debe calcular AX = 0")
    hint: str = Field(..., 
                     description="Pista sobre el error",
                     example="Revisa cuidadosamente la instrucción SUB y sus operandos")


class AssemblyAnswerRequest(BaseModel):
    """
    Solicitud para responder al juego de Ensamblador.
    
    Attributes:
        game_id: Identificador del juego
        corrected_code: Código corregido
        explanation: Explicación de la corrección
    """
    game_id: str = Field(..., 
                         description="Identificador del juego")
    corrected_code: str = Field(..., 
                              description="Código corregido",
                              example="MOV AX, 5\nADD AX, 10\nMOV BX, AX\nSUB AX, AX\n; El resultado es 0")
    explanation: Optional[str] = Field(default=None,
                                    description="Explicación de la corrección",
                                    example="La instrucción SUB AX, BX restaba BX de AX, pero necesitábamos AX - AX para obtener 0")


class AssemblyAnswerResponse(BaseModel):
    """
    Respuesta a la solución propuesta para el juego de Ensamblador.
    
    Attributes:
        correct: Si la corrección es correcta
        explanation: Explicación detallada
        correct_solution: Posible solución correcta (cuando la respuesta es incorrecta)
    """
    correct: bool = Field(..., 
                         description="Si la corrección es correcta")
    explanation: str = Field(..., 
                            description="Explicación detallada",
                            example="¡Correcto! La instrucción SUB AX, BX restaba BX de AX, lo que daba un resultado distinto de 0. Al cambiar a SUB AX, AX, siempre obtenemos 0 porque cualquier número menos sí mismo es 0.")
    correct_solution: Optional[str] = Field(default=None,
                                         description="Posible solución correcta (cuando la respuesta es incorrecta)")