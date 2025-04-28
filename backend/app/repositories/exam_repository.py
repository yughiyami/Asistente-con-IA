"""
Repositorio para la gestión de exámenes.
Proporciona métodos para almacenar y recuperar exámenes y sus respuestas.

En una implementación real, este repositorio se conectaría a una base de datos
persistente. Para esta versión, se utiliza un almacenamiento en memoria.
"""

import logging
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)


class ExamRepository:
    """
    Repositorio para almacenar y recuperar exámenes y sus respuestas.
    
    Proporciona métodos para:
    - Guardar exámenes generados
    - Recuperar exámenes previamente guardados
    - Almacenar y recuperar respuestas correctas
    """
    
    def __init__(self):
        """Inicializa el repositorio con almacenamiento en memoria."""
        # Diccionario para almacenar exámenes {exam_id: exam_data}
        self._exams: Dict[str, Dict[str, Any]] = {}
    
    async def save_exam(
        self, 
        exam_id: str, 
        questions: List[Dict[str, Any]], 
        answers: Dict[str, str],
        explanations: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Guarda un examen generado con sus preguntas y respuestas.
        
        Args:
            exam_id: Identificador único del examen
            questions: Lista de preguntas (diccionarios)
            answers: Diccionario de respuestas correctas (id_pregunta -> respuesta)
            explanations: Diccionario de explicaciones (id_pregunta -> explicación)
            
        Returns:
            ID del examen guardado
        """
        self._exams[exam_id] = {
            "id": exam_id,
            "questions": questions,
            "answers": answers,
            "explanations": explanations or {},
            "created_at": datetime.now().isoformat(),
            "attempts": []  # Lista para almacenar intentos de resolución
        }
        
        logger.info(f"Examen guardado con ID: {exam_id}")
        return exam_id
    
    async def get_exam(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un examen por su ID.
        
        Args:
            exam_id: Identificador del examen
            
        Returns:
            Datos del examen o None si no existe
        """
        exam = self._exams.get(exam_id)
        
        if not exam:
            logger.warning(f"Examen no encontrado: {exam_id}")
            return None
        
        return exam
    
    async def save_attempt(
        self, 
        exam_id: str, 
        user_id: str, 
        answers: Dict[str, str], 
        score: float,
        time_taken_seconds: Optional[int] = None
    ) -> bool:
        """
        Guarda un intento de resolución de examen.
        
        Args:
            exam_id: Identificador del examen
            user_id: Identificador del usuario
            answers: Respuestas proporcionadas
            score: Puntuación obtenida
            time_taken_seconds: Tiempo empleado en segundos
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        exam = self._exams.get(exam_id)
        
        if not exam:
            logger.warning(f"No se puede guardar intento para examen inexistente: {exam_id}")
            return False
        
        attempt = {
            "user_id": user_id,
            "answers": answers,
            "score": score,
            "time_taken_seconds": time_taken_seconds,
            "timestamp": datetime.now().isoformat()
        }
        
        exam["attempts"].append(attempt)
        return True
    
    async def get_attempts(self, exam_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera los intentos de resolución de un examen.
        
        Args:
            exam_id: Identificador del examen
            user_id: Filtrar por usuario específico (opcional)
            
        Returns:
            Lista de intentos de resolución
        """
        exam = self._exams.get(exam_id)
        
        if not exam:
            logger.warning(f"No se pueden recuperar intentos para examen inexistente: {exam_id}")
            return []
        
        attempts = exam.get("attempts", [])
        
        # Filtrar por usuario si se especifica
        if user_id:
            attempts = [a for a in attempts if a.get("user_id") == user_id]
            
        return attempts
    
    async def delete_exam(self, exam_id: str) -> bool:
        """
        Elimina un examen del repositorio.
        
        Args:
            exam_id: Identificador del examen
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if exam_id in self._exams:
            del self._exams[exam_id]
            logger.info(f"Examen eliminado: {exam_id}")
            return True
        
        logger.warning(f"Intento de eliminar examen inexistente: {exam_id}")
        return False
    
    async def list_exams(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista exámenes con paginación.
        
        Args:
            limit: Número máximo de exámenes a devolver
            offset: Número de exámenes a saltar
            
        Returns:
            Lista de exámenes (información resumida)
        """
        exams = []
        
        for exam_id, exam_data in sorted(
            self._exams.items(), 
            key=lambda x: x[1].get("created_at", ""), 
            reverse=True
        )[offset:offset+limit]:
            # Información resumida para el listado
            exams.append({
                "id": exam_id,
                "created_at": exam_data.get("created_at"),
                "question_count": len(exam_data.get("questions", [])),
                "attempt_count": len(exam_data.get("attempts", []))
            })
            
        return exams


# Instancia global del repositorio
exam_repository = ExamRepository()