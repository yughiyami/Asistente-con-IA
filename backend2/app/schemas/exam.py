"""
Esquemas para el módulo de exámenes.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from .base import DifficultyLevel


class ExamRequest(BaseModel):
    """Solicitud para generar un examen"""
    topic: str = Field(..., min_length=3, description="Tema principal del examen")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Nivel de dificultad del examen")
    num_questions: int = Field(default=5, ge=1, le=10, description="Número de preguntas a generar (máximo 10)")
    subtopics: Optional[List[str]] = Field(None, description="Subtemas específicos a incluir")


class QuestionOption(BaseModel):
    """Opción de pregunta de opción múltiple"""
    id: str = Field(..., description="Identificador de la opción (a, b, c, d)")
    text: str = Field(..., description="Texto de la opción")


class ExamQuestion(BaseModel):
    """Pregunta del examen"""
    id: str = Field(..., description="Identificador único de la pregunta")
    text: str = Field(..., description="Texto de la pregunta")
    options: List[QuestionOption] = Field(..., min_items=4, max_items=4, description="Opciones de respuesta")
    topic: str = Field(..., description="Tema específico de la pregunta")
    difficulty: DifficultyLevel = Field(..., description="Dificultad de la pregunta")


class ExamResponse(BaseModel):
    """Respuesta con el examen generado"""
    exam_id: str = Field(..., description="Identificador único del examen")
    title: str = Field(..., description="Título del examen")
    questions: List[ExamQuestion] = Field(..., description="Lista de preguntas generadas")
    time_limit_minutes: int = Field(..., description="Tiempo límite en minutos")


class ExamValidationRequest(BaseModel):
    """Solicitud de validación de examen"""
    exam_id: str = Field(..., description="Identificador del examen a validar")
    answers: Dict[str, str] = Field(..., description="Respuestas proporcionadas")
    
    @validator('answers')
    def validate_answers(cls, v):
        """Valida que las respuestas sean opciones válidas"""
        for question_id, answer in v.items():
            if answer not in ['a', 'b', 'c', 'd']:
                raise ValueError(f"Respuesta inválida '{answer}' para pregunta {question_id}")
        return v


class QuestionResult(BaseModel):
    """Resultado de una pregunta individual"""
    correct: bool = Field(..., description="Si la respuesta fue correcta")
    user_answer: str = Field(..., description="Respuesta del usuario")
    correct_answer: str = Field(..., description="Respuesta correcta")
    explanation: str = Field(..., description="Explicación de la respuesta correcta")


class ExamValidationResponse(BaseModel):
    """Respuesta de validación del examen"""
    score: float = Field(..., ge=0, le=100, description="Puntuación obtenida (0-100)")
    question_results: Dict[str, QuestionResult] = Field(..., description="Resultados por pregunta")
    feedback: str = Field(..., description="Retroalimentación general del desempeño")
    time_taken_seconds: Optional[int] = Field(None, description="Tiempo tomado en segundos")