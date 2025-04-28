"""
Endpoints para el modo Examen.
Gestiona la generación y validación de exámenes de opción múltiple.
"""

import uuid
import logging
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import ValidationError

from app.schemas.exam import (
    ExamRequest, ExamResponse, ExamValidationRequest, 
    ExamValidationResponse, Question, QuestionResult
)
from app.services.llm import llm_service
from app.repositories.exam_repository import exam_repository

# Configurar logger
logger = logging.getLogger(__name__)

# Configurar router
router = APIRouter()


@router.post("/generate", response_model=ExamResponse)
async def generate_exam(
    request: ExamRequest,
    background_tasks: BackgroundTasks,
) -> ExamResponse:
    """
    Genera un examen personalizado de arquitectura de computadoras.
    
    - Crea preguntas de opción múltiple sobre el tema especificado
    - Almacena las respuestas correctas para posterior validación
    
    Parameters:
    - **request**: Tema, dificultad y número de preguntas para el examen
    
    Returns:
    - **ExamResponse**: Examen generado con preguntas de opción múltiple
    """
    try:
        # Generar prompt para el LLM
        prompt = f"""
        Crea un examen de arquitectura de computadoras sobre el tema '{request.topic}' 
        con {request.num_questions} preguntas de opción múltiple (a-d).
        El nivel de dificultad es {request.difficulty}.
        
        {f"Enfócate en estos subtemas específicos: {', '.join(request.subtopics)}" if request.subtopics else ""}
        
        Cada pregunta debe tener exactamente 4 alternativas: a) , b) ,c) y d), donde solo una es correcta.
        
        Formato para cada pregunta:
        "P[número]: [texto de la pregunta]
        a) [alternativa a]
        b) [alternativa b]"
        
        Al final, proporciona las respuestas correctas en formato JSON:
        "{{
            "answers": {{
                "1": "a",
                "2": "b",
                ...
            }},
            "explanations": {{
                "1": "Explicación de por qué la respuesta es correcta...",
                "2": "Explicación de por qué la respuesta es correcta...",
                ...
            }}
        }}"
        """
        
        # Llamar al LLM
        llm_response = await llm_service.generate_text(prompt)
        
        # Procesar la respuesta para extraer preguntas y respuestas
        questions_part, answers_part = "", ""
        
        if "Respuestas:" in llm_response:
            questions_part, answers_part = llm_response.split("Respuestas:", 1)
        else:
            # Intentar extraer la parte JSON para las respuestas
            questions_part = llm_response
            
            # Buscar un objeto JSON en la respuesta
            try:
                answers_json = await llm_service.extract_json_from_text(llm_response)
                answers_part = json.dumps(answers_json)
            except ValueError:
                # Si no se encuentra JSON, todo es parte de las preguntas
                logger.warning("No se pudo extraer JSON de respuestas, generando respuestas aleatorias")
        
        # Crear lista de preguntas
        questions = []
        correct_answers = {}
        explanations = {}
        
        # Extraer preguntas
        question_blocks = questions_part.split("P")
        for i, q_block in enumerate(question_blocks[1:], 1):  # Ignorar el primer split que está vacío
            try:
                # Separar la pregunta y alternativas
                lines = q_block.strip().split("\n")
                
                # La primera línea contiene el número y texto de la pregunta
                qnum_text = lines[0].strip()
                if ":" in qnum_text:
                    q_num, q_text = qnum_text.split(":", 1)
                    q_text = q_text.strip()
                else:
                    q_num = str(i)
                    q_text = qnum_text
                
                # Las siguientes líneas son alternativas
                alternatives = {}
                for alt_line in lines[1:]:
                    if alt_line.startswith("a)"):
                        alternatives["a"] = alt_line[2:].strip()
                    elif alt_line.startswith("b)"):
                        alternatives["b"] = alt_line[2:].strip()
                
                # Verificar que haya al menos dos alternativas
                if len(alternatives) < 2:
                    logger.warning(f"La pregunta {q_num} no tiene suficientes alternativas")
                    continue
                
                # Crear objeto de pregunta
                questions.append(Question(
                    id=f"question_{q_num}",
                    text=q_text,
                    alternatives=alternatives
                ))
                
            except Exception as e:
                logger.error(f"Error al procesar pregunta {i}: {str(e)}")
                continue
        
        # Extraer respuestas correctas
        try:
            # Intentar parsear las respuestas como JSON
            answers_json = await llm_service.extract_json_from_text(answers_part)
            
            if "answers" in answers_json:
                correct_answers = answers_json["answers"]
            
            if "explanations" in answers_json:
                explanations = answers_json["explanations"]
            
        except Exception as e:
            logger.error(f"Error al extraer respuestas: {str(e)}")
            # Generar respuestas aleatorias para demostración
            import random
            correct_answers = {f"{i}": random.choice(["a", "b"]) for i in range(1, len(questions) + 1)}
        
        # Crear ID único para el examen
        exam_id = f"exam_{uuid.uuid4().hex}"
        
        # Convertir las respuestas al formato de IDs de preguntas
        question_answers = {}
        for i, q in enumerate(questions, 1):
            q_id = q.id
            if str(i) in correct_answers:
                question_answers[q_id] = correct_answers[str(i)]
        
        # Crear objeto para explicaciones
        question_explanations = {}
        for i, q in enumerate(questions, 1):
            q_id = q.id
            if str(i) in explanations:
                question_explanations[q_id] = explanations[str(i)]
        
        # Guardar examen y respuestas (esto se hará en segundo plano)
        background_tasks.add_task(
            exam_repository.save_exam,
            exam_id=exam_id,
            questions=[q.dict() for q in questions],
            answers=question_answers,
            explanations=question_explanations
        )
        
        # Crear título descriptivo
        exam_title = f"Examen de {request.topic} - Nivel {request.difficulty}"
        
        return ExamResponse(
            exam_id=exam_id,
            title=exam_title,
            questions=questions,
            time_limit_minutes=request.num_questions * 5  # 5 minutos por pregunta
        )
        
    except Exception as e:
        logger.error(f"Error al generar examen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al generar el examen. Por favor, inténtalo de nuevo."
        )


@router.post("/validate", response_model=ExamValidationResponse)
async def validate_exam(request: ExamValidationRequest) -> ExamValidationResponse:
    """
    Valida las respuestas de un examen y proporciona retroalimentación.
    
    Parameters:
    - **request**: ID del examen y respuestas proporcionadas
    
    Returns:
    - **ExamValidationResponse**: Resultados de la validación con puntuación y feedback
    """
    try:
        # Obtener el examen y las respuestas correctas
        exam_data = await exam_repository.get_exam(request.exam_id)
        
        if not exam_data:
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        correct_answers = exam_data.get("answers", {})
        explanations = exam_data.get("explanations", {})
        
        # Validar respuestas
        question_results = {}
        total_questions = len(correct_answers)
        correct_count = 0
        
        for q_id, user_answer in request.answers.items():
            if q_id in correct_answers:
                is_correct = correct_answers[q_id] == user_answer
                
                if is_correct:
                    correct_count += 1
                
                explanation = explanations.get(q_id, "")
                if not explanation:
                    explanation = f"La respuesta correcta es la opción {correct_answers[q_id]}."
                
                question_results[q_id] = QuestionResult(
                    is_correct=is_correct,
                    correct_answer=correct_answers[q_id],
                    explanation=explanation
                )
        
        # Calcular puntuación
        score = 0 if total_questions == 0 else (correct_count / total_questions) * 100
        
        # Generar feedback general
        if score >= 90:
            feedback = "¡Excelente! Tienes un dominio sobresaliente de este tema."
        elif score >= 70:
            feedback = "¡Buen trabajo! Comprendes bien los conceptos, pero hay algunas áreas para mejorar."
        elif score >= 50:
            feedback = "Aprobado. Tienes conocimientos básicos, pero necesitas reforzar varios conceptos."
        else:
            feedback = "Necesitas estudiar más este tema. Revisa los materiales del curso y vuelve a intentarlo."
        
        return ExamValidationResponse(
            score=score,
            question_results=question_results,
            feedback=feedback,
            time_taken_seconds=None  # Este valor podría ser proporcionado por el frontend
        )
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
        
    except Exception as e:
        logger.error(f"Error al validar examen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al validar el examen. Por favor, inténtalo de nuevo."
        )