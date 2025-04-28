from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.db.base import get_db
from app.schemas.schemas import ChatRequest, ChatResponse, ExamCreate, ExamResponse, SubmitExamRequest, ExamResult, GameRequest, GameAction, GameState
from backend.app.services.ia import ai_service
from app.services.image_service import image_service
import app.models.models as models
import uuid

router = APIRouter()

# Endpoint para chat
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal para el chatbot
    """
    # Crear nueva sesión si no existe
    session_id = request.session_id or str(uuid.uuid4())
    
    # Obtener respuesta de IA
    ai_response = await ai_service.get_chat_response(
        message=request.message,
        session_id=session_id,
        mode=request.mode
    )
    
    # Buscar imágenes si hay consultas de imágenes
    images = []
    if ai_response.get("image_queries"):
        for img_query in ai_response.get("image_queries", [])[:3]:  # Limitar a 3 imágenes
            query = img_query.get("query", "")
            description = img_query.get("description", "")
            
            # Buscar imágenes
            img_results = await image_service.search_images(query, num_images=1)
            if img_results:
                for img in img_results:
                    img["alt_text"] = description or img["alt_text"]
                    images.append(img)
    
    # Guardar mensaje en la base de datos
    db_message = models.Message(
        session_id=session_id,
        content=request.message,
        role="user"
    )
    db.add(db_message)
    
    # Guardar respuesta en la base de datos
    db_response = models.Message(
        session_id=session_id,
        content=ai_response.get("text", ""),
        role="assistant"
    )
    db.add(db_response)
    db.commit()
    
    return ChatResponse(
        text=ai_response.get("text", ""),
        images=images,
        special_content=None
    )

# Endpoints para exámenes
@router.post("/exam/generate", response_model=ExamResponse)
async def generate_exam(topic: str, difficulty: str = "medium", db: Session = Depends(get_db)):
    """
    Genera un examen sobre un tema específico
    """
    try:
        # Generar examen con IA
        exam_data = await ai_service.generate_exam(topic, difficulty)
        
        # Crear examen en la base de datos
        db_exam = models.Exam(
            title=exam_data.get("title", f"Examen sobre {topic}"),
            description=exam_data.get("description", ""),
            topic=topic,
            difficulty=difficulty
        )
        db.add(db_exam)
        db.flush()
        
        # Crear preguntas
        db_questions = []
        for question in exam_data.get("questions", []):
            db_question = models.Question(
                exam_id=db_exam.id,
                question_text=question.get("question_text", ""),
                question_type=question.get("question_type", "multiple_choice"),
                options=question.get("options"),
                correct_answer=question.get("correct_answer", ""),
                explanation=question.get("explanation", ""),
                points=question.get("points", 1)
            )
            db.add(db_question)
            db_questions.append(db_question)
        
        db.commit()
        
        # Refrescar para obtener IDs
        for q in db_questions:
            db.refresh(q)
        
        # Construir respuesta
        return ExamResponse(
            id=db_exam.id,
            title=db_exam.title,
            description=db_exam.description,
            topic=db_exam.topic,
            difficulty=db_exam.difficulty,
            questions=[
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "options": q.options,
                    "points": q.points
                }
                for q in db_questions
            ]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al generar examen: {str(e)}")

@router.post("/exam/submit", response_model=ExamResult)
async def submit_exam(request: SubmitExamRequest, db: Session = Depends(get_db)):
    """
    Evalúa las respuestas de un examen
    """
    try:
        # Obtener examen y preguntas
        exam = db.query(models.Exam).filter(models.Exam.id == request.exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        questions = db.query(models.Question).filter(models.Question.exam_id == exam.id).all()
        
        # Preparar datos para evaluación
        exam_data = {
            "title": exam.title,
            "description": exam.description,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "points": q.points
                }
                for q in questions
            ]
        }
        
        # Evaluar respuestas
        evaluation = await ai_service.evaluate_exam(exam_data, request.answers)
        
        # Crear intento de examen en la base de datos
        db_attempt = models.ExamAttempt(
            exam_id=exam.id,
            answers=request.answers,
            score=evaluation.get("score", 0)
        )
        db.add(db_attempt)
        db.commit()
        
        return ExamResult(
            exam_id=exam.id,
            score=evaluation.get("score", 0),
            total_points=evaluation.get("total_points", 0),
            percentage=evaluation.get("percentage", 0),
            question_results=evaluation.get("question_results", []),
            feedback=evaluation.get("feedback", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al evaluar examen: {str(e)}")

# Endpoints para juegos
@router.post("/game/initialize", response_model=GameState)
async def initialize_game(request: GameRequest):
    """
    Inicializa un nuevo juego educativo
    """
    try:
        game_state = await ai_service.initialize_game(request.game_type, request.config)
        
        # Generar ID de juego
        game_id = str(uuid.uuid4())
        
        return GameState(
            game_id=game_id,
            game_type=request.game_type,
            state=game_state,
            completed=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al inicializar juego: {str(e)}")

@router.post("/game/{game_id}/action", response_model=GameState)
async def game_action(game_id: str, action: GameAction):
    """
    Procesa una acción en un juego
    """
    try:
        # En una implementación real, obtendrías el estado del juego de la base de datos
        # Aquí simulamos un estado simple para demonstración
        game_state = {
            "type": action.data.get("game_type", "unknown"),
            "game_id": game_id
        }
        
        # Procesar acción
        result = await ai_service.process_game_action(game_state, {
            "action": action.action,
            "data": action.data
        })
        
        return GameState(
            game_id=game_id,
            game_type=result.get("state", {}).get("type", "unknown"),
            state=result.get("state", {}),
            message=result.get("message"),
            completed=result.get("state", {}).get("completed", False),
            score=result.get("state", {}).get("score")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar acción de juego: {str(e)}")