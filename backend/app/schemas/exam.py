"""
Esquemas Pydantic para las solicitudes y respuestas del modo Examen.
Define la estructura para la generación, presentación y validación de exámenes.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class DifficultyLevel(str, Enum):
    """Niveles de dificultad disponibles para los exámenes."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ExamRequest(BaseModel):
    """
    Solicitud para generar un examen.
    
    Attributes:
        topic: Tema principal del examen
        difficulty: Nivel de dificultad
        num_questions: Número de preguntas a generar (máximo 10)
        subtopics: Lista opcional de subtemas específicos
    """
    topic: str = Field(..., 
                       description="Tema principal del examen",
                       example="Arquitectura de microprocesadores")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM,
                                      description="Nivel de dificultad del examen")
    num_questions: int = Field(default=5, ge=1, le=10,
                             description="Número de preguntas a generar (máximo 10)")
    subtopics: Optional[List[str]] = Field(default=None,
                                         description="Subtemas específicos a incluir",
                                         example=["Pipeline", "Memoria caché"])


class Alternative(BaseModel):
    """
    Alternativa para una pregunta de opción múltiple.
    
    Attributes:
        id: Identificador único de la alternativa (a, b, c, etc.)
        text: Texto de la alternativa
    """
    id: str = Field(..., 
                    description="Identificador único de la alternativa",
                    example="a")
    text: str = Field(..., 
                      description="Texto de la alternativa",
                      example="La unidad que realiza operaciones aritméticas y lógicas")


class Question(BaseModel):
    """
    Pregunta de examen de opción múltiple.
    
    Attributes:
        id: Identificador único de la pregunta
        text: Texto de la pregunta
        alternatives: Diccionario de alternativas disponibles
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                  description="Identificador único de la pregunta")
    text: str = Field(..., 
                      description="Texto de la pregunta",
                      example="¿Cuál es la función principal de la ALU en un procesador?")
    alternatives: Dict[str, str] = Field(...,
                                       description="Alternativas de respuesta",
                                       example={
                                           "a": "La unidad que realiza operaciones aritméticas y lógicas",
                                           "b": "El componente que almacena temporalmente los datos"
                                       })


class ExamResponse(BaseModel):
    """
    Respuesta con el examen generado.
    
    Attributes:
        exam_id: Identificador único del examen
        title: Título descriptivo del examen
        questions: Lista de preguntas generadas
        time_limit_minutes: Tiempo límite recomendado en minutos
    """
    exam_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                       description="Identificador único del examen")
    title: str = Field(..., 
                       description="Título descriptivo del examen",
                       example="Examen de Arquitectura de Microprocesadores")
    questions: List[Question] = Field(...,
                                    description="Lista de preguntas generadas")
    time_limit_minutes: int = Field(default=30,
                                  description="Tiempo límite recomendado en minutos")


class ExamValidationRequest(BaseModel):
    """
    Solicitud para validar las respuestas de un examen.
    
    Attributes:
        exam_id: Identificador del examen
        answers: Diccionario de respuestas (ID de pregunta -> ID de alternativa)
    """
    exam_id: str = Field(..., 
                         description="Identificador del examen a validar")
    answers: Dict[str, str] = Field(...,
                                  description="Respuestas proporcionadas",
                                  example={
                                      "question_1": "a",
                                      "question_2": "b"
                                  })


class QuestionResult(BaseModel):
    """
    Resultado de una pregunta individual.
    
    Attributes:
        is_correct: Si la respuesta es correcta
        correct_answer: ID de la alternativa correcta
        explanation: Explicación sobre la respuesta correcta
    """
    is_correct: bool = Field(..., 
                            description="Si la respuesta es correcta")
    correct_answer: str = Field(..., 
                               description="ID de la alternativa correcta",
                               example="a")
    explanation: str = Field(..., 
                            description="Explicación sobre la respuesta correcta",
                            example="La ALU (Unidad Aritmético Lógica) es responsable de realizar operaciones matemáticas y lógicas en un procesador.")


class ExamValidationResponse(BaseModel):
    """
    Respuesta con los resultados de la validación del examen.
    
    Attributes:
        score: Puntuación obtenida (0-100)
        question_results: Resultados detallados por pregunta
        feedback: Retroalimentación general sobre el desempeño
        time_taken_seconds: Tiempo empleado en segundos
    """
    score: float = Field(..., 
                         description="Puntuación obtenida (0-100)",
                         ge=0, le=100)
    question_results: Dict[str, QuestionResult] = Field(...,
                                                      description="Resultados detallados por pregunta")
    feedback: str = Field(..., 
                          description="Retroalimentación general sobre el desempeño",
                          example="Buen trabajo! Demuestra comprensión de los conceptos básicos, pero podría mejorar en temas relacionados con memoria caché.")
    time_taken_seconds: Optional[int] = Field(default=None,
                                            description="Tiempo empleado en segundos")