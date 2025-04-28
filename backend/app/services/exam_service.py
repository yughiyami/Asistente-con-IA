"""
Servicio para el modo Examen.
Gestiona la generación y validación de exámenes.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional

from app.services.llm import llm_service
from app.repositories.exam_repository import exam_repository
from app.schemas.exam import ExamResponse, ExamValidationResponse, Question, QuestionResult

# Configurar logger
logger = logging.getLogger(__name__)


class ExamService:
    """
    Servicio para gestionar el modo Examen.
    
    Proporciona métodos para:
    - Generar exámenes personalizados
    - Validar respuestas de estudiantes
    - Proporcionar retroalimentación educativa
    """
    
    def __init__(self):
        """Inicializa el servicio de examen."""
        pass
    
    async def generate_exam(
        self, 
        topic: str, 
        difficulty: str = "medium", 
        num_questions: int = 10,
        subtopics: Optional[List[str]] = None
    ) -> ExamResponse:
        """
        Genera un examen personalizado según los parámetros especificados.
        
        Args:
            topic: Tema principal del examen
            difficulty: Nivel de dificultad ("easy", "medium", "hard")
            num_questions: Número de preguntas a generar
            subtopics: Lista opcional de subtemas específicos
            
        Returns:
            Examen generado con preguntas y metadatos
        """
        try:
            # Generar examen utilizando el servicio LLM
            exam_data = await llm_service.generate_exam(
                topic=topic,
                difficulty=difficulty,
                question_count=num_questions
            )
            
            # Verificar el resultado
            if not exam_data or "questions" not in exam_data or not exam_data["questions"]:
                raise ValueError("No se pudieron generar preguntas para el examen")
            
            # Crear ID único para el examen
            exam_id = f"exam_{uuid.uuid4().hex}"
            
            # Preparar preguntas en el formato adecuado
            questions = []
            answers = {}
            explanations = {}
            
            for i, q_data in enumerate(exam_data["questions"]):
                # Generar ID único para cada pregunta
                q_id = f"question_{i+1}"
                
                # Construir objeto de pregunta según el tipo
                if q_data["question_type"] == "multiple_choice":
                    # Crear pregunta de opción múltiple
                    question = Question(
                        id=q_id,
                        text=q_data["question_text"],
                        alternatives={
                            chr(97 + j): option  # a, b, c, d...
                            for j, option in enumerate(q_data["options"])
                        }
                    )
                    
                    # Convertir el índice numérico a letra (0 -> 'a', 1 -> 'b', etc.)
                    correct_index = int(q_data["correct_answer"])
                    correct_letter = chr(97 + correct_index)
                    answers[q_id] = correct_letter
                    
                elif q_data["question_type"] == "open_ended":
                    # Crear pregunta de respuesta abierta
                    question = Question(
                        id=q_id,
                        text=q_data["question_text"],
                        alternatives={}  # Sin alternativas para preguntas abiertas
                    )
                   
                    answers[q_id] = q_data["correct_answer"]
                
                # Guardar la explicación
                explanations[q_id] = q_data["explanation"]
                
                # Agregar pregunta a la lista
                questions.append(question)
            
            # Guardar examen en el repositorio
            await exam_repository.save_exam(
                exam_id=exam_id,
                questions=[q.dict() for q in questions],
                answers=answers,
                explanations=explanations
            )
            
            # Crear título descriptivo
            exam_title = exam_data.get("title", f"Examen de {topic} - Nivel {difficulty}")
            
            # Preparar respuesta
            return ExamResponse(
                exam_id=exam_id,
                title=exam_title,
                questions=questions,
                time_limit_minutes=num_questions * 5  # 5 minutos por pregunta (ajustable)
            )
            
        except Exception as e:
            logger.error(f"Error al generar examen: {str(e)}")
            
            # Crear un examen mínimo para no fallar completamente
            return ExamResponse(
                exam_id=f"error_{uuid.uuid4().hex}",
                title=f"Error al generar examen sobre {topic}",
                questions=[],
                time_limit_minutes=0
            )
    
    async def validate_exam(
        self, 
        exam_id: str, 
        answers: Dict[str, str]
    ) -> ExamValidationResponse:
        """
        Valida las respuestas proporcionadas para un examen y genera retroalimentación.
        
        Args:
            exam_id: Identificador del examen
            answers: Diccionario de respuestas (ID de pregunta -> respuesta)
            
        Returns:
            Resultado de la validación con puntuación y retroalimentación
        """
        try:
            # Obtener el examen y sus respuestas correctas
            exam_data = await exam_repository.get_exam(exam_id)
            
            if not exam_data:
                raise ValueError(f"Examen no encontrado: {exam_id}")
            
            # Extraer datos relevantes
            questions = exam_data.get("questions", [])
            correct_answers = exam_data.get("answers", {})
            explanations = exam_data.get("explanations", {})
            
            # Identificar preguntas abiertas vs opción múltiple
            question_types = {}
            for q in questions:
                q_id = q.get("id", "")
                # Si tiene alternativas, es de opción múltiple
                question_types[q_id] = "multiple_choice" if q.get("alternatives") else "open_ended"
            
            # Evaluar respuestas
            if len(questions) == 0:
                return ExamValidationResponse(
                    score=0,
                    question_results={},
                    feedback="No se pudieron validar las respuestas. El examen no contiene preguntas.",
                    time_taken_seconds=None
                )
            
            # Para preguntas de opción múltiple, hacemos validación directa
            # Para preguntas abiertas, usamos el LLM
            
            # 1. Primero procesamos las preguntas de opción múltiple
            question_results = {}
            score = 0
            total_points = len(questions)  # Por defecto, cada pregunta vale 1 punto
            
            for q in questions:
                q_id = q.get("id", "")
                q_type = question_types.get(q_id, "multiple_choice")
                
                # Si la pregunta no fue respondida
                if q_id not in answers:
                    question_results[q_id] = QuestionResult(
                        is_correct=False,
                        correct_answer=correct_answers.get(q_id, ""),
                        explanation=f"Pregunta no respondida. {explanations.get(q_id, '')}"
                    )
                    continue
                
                # Procesar según el tipo
                user_answer = answers[q_id]
                
                if q_type == "multiple_choice":
                    # Comparación directa para opción múltiple
                    is_correct = user_answer.lower() == correct_answers.get(q_id, "").lower()
                    
                    if is_correct:
                        score += 1
                    
                    question_results[q_id] = QuestionResult(
                        is_correct=is_correct,
                        correct_answer=correct_answers.get(q_id, ""),
                        explanation=explanations.get(q_id, "")
                    )
                else:
                    # Para preguntas abiertas, evaluamos con el LLM
                    try:
                        # Obtener el texto de la pregunta
                        question_text = next((q.get("text", "") for q in questions if q.get("id") == q_id), "")
                        
                        # Preparar datos para la evaluación
                        eval_data = {
                            "questions": [{
                                "question_text": question_text,
                                "question_type": "open_ended",
                                "correct_answer": correct_answers.get(q_id, ""),
                                "explanation": explanations.get(q_id, ""),
                                "id": q_id
                            }]
                        }
                        
                        # Evaluar usando el LLM
                        eval_result = await llm_service.evaluate_exam(
                            exam_data=eval_data, 
                            user_answers={q_id: user_answer}
                        )
                        
                        # Extraer resultado
                        result = eval_result.get("question_results", [])[0]
                        points = result.get("points_earned", 0)
                        score += points
                        
                        # Crear resultado
                        question_results[q_id] = QuestionResult(
                            is_correct=result.get("correct", False),
                            correct_answer=correct_answers.get(q_id, ""),
                            explanation=f"{explanations.get(q_id, '')} \n\nAnálisis de tu respuesta: {result.get('accuracy', 0) * 100:.0f}% de precisión."
                        )
                        
                    except Exception as e:
                        logger.error(f"Error al evaluar pregunta abierta {q_id}: {str(e)}")
                        
                        # Fallback en caso de error
                        question_results[q_id] = QuestionResult(
                            is_correct=None,  # Desconocido
                            correct_answer=correct_answers.get(q_id, ""),
                            explanation=f"Error al evaluar. La respuesta esperada era: {correct_answers.get(q_id, '')}"
                        )
            
            # Calcular puntuación final
            percentage = (score / total_points) * 100 if total_points > 0 else 0
            
            # Generar retroalimentación general basada en la puntuación
            feedback = ""
            if percentage >= 90:
                feedback = "¡Excelente trabajo! Demuestras un dominio sobresaliente de los conceptos evaluados."
            elif percentage >= 70:
                feedback = "¡Buen trabajo! Has demostrado un buen nivel de comprensión aunque hay algunas áreas que podrías revisar."
            elif percentage >= 50:
                feedback = "Has aprobado, pero es recomendable reforzar varios conceptos para mejorar tu comprensión."
            else:
                feedback = "Necesitas dedicar más tiempo a estudiar estos temas. Revisa los materiales del curso y las explicaciones proporcionadas."
            
            return ExamValidationResponse(
                score=percentage,
                question_results=question_results,
                feedback=feedback,
                time_taken_seconds=None  # Este valor podría ser proporcionado por el frontend
            )
            
        except Exception as e:
            logger.error(f"Error al validar examen: {str(e)}")
            
            return ExamValidationResponse(
                score=0,
                question_results={},
                feedback=f"Se produjo un error al validar el examen. Por favor, intenta nuevamente.",
                time_taken_seconds=None
            )


# Instancia global del servicio
exam_service = ExamService()