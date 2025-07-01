"""
Servicio para interactuar con Google Gemini AI.
Maneja generación de respuestas educativas y contenido para juegos.
"""

import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Servicio para interactuar con Google Gemini"""
    
    def __init__(self):
        """Inicializa el servicio con la API key"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    async def generate_chat_response(
        self, 
        query: str, 
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Genera una respuesta educativa para consultas sobre arquitectura de computadoras.
        
        Args:
            query: Pregunta del usuario
            context: Contexto adicional de PDFs
            history: Historial de conversación
            
        Returns:
            Respuesta generada por Gemini
        """
        # Construir el prompt
        prompt = self._build_chat_prompt(query, context, history)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {str(e)}")
            raise
    
    async def generate_exam_questions(
        self, 
        topic: str, 
        difficulty: str,
        num_questions: int,
        subtopics: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Genera preguntas de opción múltiple para un examen.
        
        Returns:
            Lista de preguntas con formato específico
        """
        prompt = self._build_exam_prompt(topic, difficulty, num_questions, subtopics)
        try:
            response = self.model.generate_content(prompt)
            # Parsear la respuesta JSON

            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remover ```json
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remover ```
            cleaned_text = cleaned_text.strip()
            # Parsear JSON limpio
            questions_data = json.loads(cleaned_text)

            return questions_data['questions']
        
        except Exception as e:
            logger.error(f"Error generando preguntas: {str(e)}")
            raise
    
    async def generate_hangman_word(self, topic: Optional[str], difficulty: str) -> Dict:
        """
        Genera una palabra para el juego de ahorcado.
        
        Returns:
            Diccionario con palabra, pista y argumento educativo
        """
        prompt = self._build_hangman_prompt(topic, difficulty)
        
        try:
            response = self.model.generate_content(prompt)
            
            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remover ```json
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remover ```
            cleaned_text = cleaned_text.strip()
            # Parsear JSON limpio
            questions_data = json.loads(cleaned_text)
            

            return questions_data
        except Exception as e:
            logger.error(f"Error generando palabra para ahorcado: {str(e)}")
            raise
    
    async def generate_wordle_word(self, topic: Optional[str], difficulty: str) -> Dict:
        """
        Genera una palabra de 5 letras para Wordle.
        
        Returns:
            Diccionario con palabra y pista temática
        """
        prompt = self._build_wordle_prompt(topic, difficulty)
        
        try:
            response = self.model.generate_content(prompt)

            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remover ```json
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remover ```
            cleaned_text = cleaned_text.strip()
            # Parsear JSON limpio
            questions_data = json.loads(cleaned_text)

            return  questions_data
        except Exception as e:
            logger.error(f"Error generando palabra para Wordle: {str(e)}")
            raise
    
    def _build_chat_prompt(
        self, 
        query: str, 
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Construye el prompt para chat"""
        prompt = f"""Eres un profesor experto en arquitectura de computadoras. 
        Responde de manera educativa, clara y detallada.
        
        Contexto de conversación anterior:
        {self._format_history(history) if history else "Sin historial previo"}
        
        Contexto adicional de documentos:
        {context if context else "Sin contexto adicional"}
        
        Pregunta del estudiante: {query}
        
        Proporciona una respuesta completa que:
        1. Sea técnicamente precisa
        2. Use ejemplos cuando sea apropiado
        3. Incluya referencias a conceptos fundamentales
        4. Sea accesible para estudiantes universitarios
        """
        return prompt
    
    def _build_exam_prompt(
        self, 
        topic: str, 
        difficulty: str,
        num_questions: int,
        subtopics: Optional[List[str]] = None
    ) -> str:
        """Construye el prompt para generar examen"""
        subtopics_str = ", ".join(subtopics) if subtopics else "todos los aspectos relevantes"
        
        prompt = f"""Genera {num_questions} preguntas de opción múltiple sobre {topic} 
        con nivel de dificultad {difficulty}.
        
        Subtemas a cubrir: {subtopics_str}
        
        IMPORTANTE: Responde SOLO con un JSON válido con el siguiente formato exacto:
        {{
            "questions": [
                {{
                    "text": "texto de la pregunta",
                    "options": [
                        {{"id": "a", "text": "opción A"}},
                        {{"id": "b", "text": "opción B"}},
                        {{"id": "c", "text": "opción C"}},
                        {{"id": "d", "text": "opción D"}}
                    ],
                    "correct_answer": "a",
                    "explanation": "explicación de por qué es correcta",
                    "topic": "subtema específico",
                    "difficulty": "{difficulty}"
                }}
            ]
        }}
        
        Asegúrate de que:
        1. Las preguntas sean técnicamente precisas
        2. Las opciones incorrectas sean plausibles
        3. Cubran diferentes aspectos del tema
        4. Sean apropiadas para el nivel de dificultad
        """
        return prompt
    
    def _build_hangman_prompt(self, topic: Optional[str], difficulty: str) -> str:
        """Construye el prompt para generar palabra de ahorcado"""
        topic_str = f"relacionada con {topic}" if topic else "de arquitectura de computadoras"
        length_range = {
            "easy": "4-6",
            "medium": "6-8", 
            "hard": "8-12"
        }.get(difficulty, "6-8")
        
        prompt = f"""Genera una palabra {topic_str} para el juego de ahorcado.
        La palabra debe tener entre {length_range} letras.
        
        Responde SOLO con un JSON con el siguiente formato:
        {{
            "word": "palabra",
            "clue": "pista breve pero útil",
            "argument": "explicación educativa de por qué este concepto es importante en arquitectura de computadoras"
        }}
        
        La palabra debe ser:
        1. Un término técnico real usado en arquitectura de computadoras
        2. Sin espacios ni caracteres especiales
        3. Apropiada para el nivel de dificultad
        """
        return prompt
    
    def _build_wordle_prompt(self, topic: Optional[str], difficulty: str) -> str:
        """Construye el prompt para generar palabra de Wordle"""
        topic_str = f"relacionada con {topic}" if topic else "de arquitectura de computadoras"
        
        prompt = f"""Genera una palabra de EXACTAMENTE 5 letras {topic_str} para Wordle.
        Nivel de dificultad: {difficulty}
        
        Responde SOLO con un JSON con el siguiente formato:
        {{
            "word": "palabra",
            "topic_hint": "pista temática sin revelar la palabra",
            "explanation": "explicación del concepto para mostrar al final del juego"
        }}
        
        La palabra debe ser:
        1. Exactamente 5 letras
        2. Un término real de arquitectura de computadoras
        3. Sin números ni caracteres especiales
        4. Común para dificultad fácil, más técnica para difícil
        """
        return prompt
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Formatea el historial de conversación"""
        if not history:
            return ""
        
        formatted = []
        for msg in history[-5:]:  # Últimos 5 mensajes
            role = "Usuario" if msg['role'] == 'user' else "Asistente"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)