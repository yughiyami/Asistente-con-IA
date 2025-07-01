"""
Router para endpoints de exámenes.
Maneja generación y validación de exámenes.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import uuid
import logging

from app.schemas.exam import (
    ExamRequest, ExamResponse, ExamValidationRequest, 
    ExamValidationResponse, ExamQuestion, QuestionOption,
    QuestionResult
)
from app.schemas.base import DifficultyLevel
from app.services.gemini_service import GeminiService
from app.services.redis_service import RedisService
from app.core.dependencies import get_gemini_service, get_redis_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/exam", tags=["exam"])


@router.post("/generate", response_model=ExamResponse)
async def generate_exam(
    request: ExamRequest,
    gemini: GeminiService = Depends(get_gemini_service),
    redis: RedisService = Depends(get_redis_service)
) -> ExamResponse:
    """
    Genera un examen personalizado de arquitectura de computadoras.
    
    - Crea preguntas de opción múltiple sobre el tema especificado
    - Almacena las respuestas correctas para posterior validación
    - Ajusta el tiempo límite según la dificultad
    """
    try:
        # Generar ID único para el examen
        exam_id = str(uuid.uuid4())
        
        # Generar preguntas con Gemini
        questions_data = await gemini.generate_exam_questions(
            topic=request.topic,
            difficulty=request.difficulty.value,
            num_questions=request.num_questions,
            subtopics=request.subtopics
        )
        
        # Procesar preguntas al formato del esquema
        questions = []
        correct_answers = {}
        
        for i, q_data in enumerate(questions_data):
            question_id = f"question_{i+1}"
            
            # Crear opciones
            options = [
                QuestionOption(id=opt["id"], text=opt["text"])
                for opt in q_data["options"]
            ]
            
            # Crear pregunta
            question = ExamQuestion(
                id=question_id,
                text=q_data["text"],
                options=options,
                topic=q_data.get("topic", request.topic),
                difficulty=request.difficulty
            )
            questions.append(question)
            
            # Guardar respuesta correcta y explicación
            correct_answers[question_id] = {
                "correct": q_data["correct_answer"],
                "explanation": q_data["explanation"]
            }
        
        # Determinar tiempo límite según dificultad
        time_limits = {
            DifficultyLevel.EASY: settings.exam_time_limit_easy,
            DifficultyLevel.MEDIUM: settings.exam_time_limit_medium,
            DifficultyLevel.HARD: settings.exam_time_limit_hard
        }
        time_limit = time_limits.get(request.difficulty, settings.exam_time_limit_medium)
        
        # Guardar examen en Redis
        exam_data = {
            "exam_id": exam_id,
            "title": f"Examen de {request.topic}",
            "topic": request.topic,
            "difficulty": request.difficulty.value,
            "questions": [q.dict() for q in questions],
            "correct_answers": correct_answers,
            "time_limit_minutes": time_limit,
            "created_at": str(uuid.uuid4())  # Timestamp simulado
        }
        
        await redis.save_exam(exam_id, exam_data)
        
        return ExamResponse(
            exam_id=exam_id,
            title=f"Examen de {request.topic}",
            questions=questions,
            time_limit_minutes=time_limit
        )
        
    except Exception as e:
        logger.error(f"Error generando examen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el examen: {str(e)}"
        )


@router.post("/validate", response_model=ExamValidationResponse)
async def validate_exam(
    request: ExamValidationRequest,
    redis: RedisService = Depends(get_redis_service)
) -> ExamValidationResponse:
    """
    Valida las respuestas de un examen y proporciona retroalimentación.
    
    - Compara las respuestas del usuario con las correctas
    - Calcula la puntuación obtenida
    - Proporciona explicaciones para cada pregunta
    - Genera retroalimentación general sobre el desempeño
    """
    try:
        # Obtener datos del examen
        exam_data = await redis.get_exam(request.exam_id)
        if not exam_data:
            raise HTTPException(
                status_code=404,
                detail="Examen no encontrado"
            )
        
        # Validar respuestas
        correct_answers = exam_data["correct_answers"]
        question_results = {}
        correct_count = 0
        total_questions = len(correct_answers)
        
        # Analizar respuestas por tema para retroalimentación
        topics_performance = {}
        
        for question_id, user_answer in request.answers.items():
            if question_id not in correct_answers:
                continue
            
            correct_data = correct_answers[question_id]
            is_correct = user_answer == correct_data["correct"]
            
            if is_correct:
                correct_count += 1
            
            # Crear resultado de la pregunta
            question_results[question_id] = QuestionResult(
                correct=is_correct,
                user_answer=user_answer,
                correct_answer=correct_data["correct"],
                explanation=correct_data["explanation"]
            )
            
            # Rastrear desempeño por tema
            question = next((q for q in exam_data["questions"] if q["id"] == question_id), None)
            if question:
                topic = question.get("topic", exam_data["topic"])
                if topic not in topics_performance:
                    topics_performance[topic] = {"correct": 0, "total": 0}
                topics_performance[topic]["total"] += 1
                if is_correct:
                    topics_performance[topic]["correct"] += 1
        
        # Calcular puntuación
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Generar retroalimentación personalizada
        feedback = _generate_exam_feedback(
            score=score,
            topics_performance=topics_performance,
            difficulty=exam_data.get("difficulty", "medium")
        )
        
        return ExamValidationResponse(
            score=round(score, 2),
            question_results=question_results,
            feedback=feedback,
            time_taken_seconds=None  # Podría implementarse con timestamps
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validando examen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al validar el examen: {str(e)}"
        )


def _generate_exam_feedback(
    score: float, 
    topics_performance: Dict[str, Dict[str, int]],
    difficulty: str
) -> str:
    """
    Genera retroalimentación personalizada basada en el desempeño.
    
    Args:
        score: Puntuación obtenida (0-100)
        topics_performance: Desempeño por tema
        difficulty: Dificultad del examen
        
    Returns:
        Retroalimentación personalizada
    """
    # Mensaje base según puntuación
    if score >= 90:
        base_message = "¡Excelente trabajo! Demuestras un dominio sólido de los conceptos."
    elif score >= 80:
        base_message = "¡Muy bien! Tienes una buena comprensión de los temas."
    elif score >= 70:
        base_message = "Buen trabajo. Hay algunos conceptos que podrías reforzar."
    elif score >= 60:
        base_message = "Resultado aceptable, pero necesitas estudiar más algunos temas."
    else:
        base_message = "Necesitas dedicar más tiempo al estudio de estos conceptos."
    
    # Analizar temas débiles
    weak_topics = []
    strong_topics = []
    
    for topic, performance in topics_performance.items():
        topic_score = (performance["correct"] / performance["total"]) * 100
        if topic_score < 60:
            weak_topics.append(topic)
        elif topic_score >= 80:
            strong_topics.append(topic)
    
    # Construir mensaje detallado
    feedback_parts = [base_message]
    
    if strong_topics:
        feedback_parts.append(f"Demuestras fortaleza en: {', '.join(strong_topics)}.")
    
    if weak_topics:
        feedback_parts.append(f"Te recomiendo repasar: {', '.join(weak_topics)}.")
    
    # Recomendaciones según dificultad y puntuación
    if difficulty == "easy" and score < 80:
        feedback_parts.append("Asegúrate de dominar los conceptos básicos antes de avanzar.")
    elif difficulty == "hard" and score >= 70:
        feedback_parts.append("¡Buen desempeño en un examen desafiante!")
    
    return " ".join(feedback_parts)