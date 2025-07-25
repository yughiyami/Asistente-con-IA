"""
Servicio para interactuar con Google Gemini AI.
Maneja generación de respuestas educativas y contenido para juegos.
"""

import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
import json
import logging
import re
from app.core.config import settings
from app.schemas.base import ProcessingMode
from vertexai.generative_models import GenerativeModel, Part

logger = logging.getLogger(__name__)


class GeminiService:
    """Servicio para interactuar con Google Gemini"""
    
    def __init__(self):
        """Inicializa el servicio con la API key"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.processing_mode = ProcessingMode.FREE 
        self.vision_model = None 
        try:
            import vertexai
            logger.info("Inicializando Gemini Vision...")
            vertexai.init(project=settings.gcp_project_id, location="us-central1")
            self.vision_model = GenerativeModel("gemini-2.5-flash")
            logger.info("Gemini Vision inicializado correctamente.")
        except Exception as e:
            self.vision_model = None
            logger.warning(f"Gemini Vision no disponible. Usando modo texto solo.::::: {str(e)}")



    # Agrega estos métodos
    def set_processing_mode(self, mode: ProcessingMode):
        """Cambia el modo de procesamiento"""
        self.processing_mode = mode
        logger.info(f"Modo de procesamiento cambiado a: {mode}")

    def get_processing_mode(self) -> ProcessingMode:
        """Obtiene el modo de procesamiento actual"""
        return self.processing_mode

    async def generate_chat_response_with_pdfs(
        self, 
        query: str, 
        pdf_paths: List[Dict],
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Genera respuesta usando PDFs como base de conocimiento.
        Usa Gemini 1.5 Flash que soporta PDFs nativamente.
        """
        if not self.vision_model:
            # Fallback a modo texto si no hay vision model
            return await self.generate_chat_response(query, None, history)
        
        # Construir partes del contenido
        contents = []
        
        # Agregar PDFs
        for pdf_info in pdf_paths:
            pdf_part = Part.from_uri(
                uri=f"file://{pdf_info['path']}",
                mime_type="application/pdf"
            )
            contents.append(pdf_part)
        
        # Agregar prompt
        prompt = f"""Eres un profesor experto en arquitectura de computadoras.
        IMPORTANTE: Debes responder ÚNICAMENTE basándote en la información contenida en los documentos PDF proporcionados.
        Si la información solicitada no está en los documentos, debes indicarlo claramente.
        NO uses conocimiento externo a los documentos.
        
        Pregunta del estudiante: {query}
        
        Responde de manera educativa y clara, citando las secciones relevantes de los documentos cuando sea posible.
        """
        
        contents.append(prompt)
        
        try:
            response = self.vision_model.generate_content(contents)
            return response.text
        except Exception as e:
            logger.error(f"Error con Gemini Vision: {str(e)}")
            # Fallback a extraer texto
            return "Lo siento, hubo un error procesando los documentos PDF. Por favor, intenta de nuevo."
    def _clean_json_response(self, response_text: str, expected_structure: str = "questions") -> Dict:
        """ Limpia y corrige respuestas JSON mal formateadas de Gemini  Args:"""
        # Intentar parsear directamente
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Intentar extraer JSON del texto
        try:
            # Buscar el primer { y el último }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Intentar corregir errores comunes
        try:
            # Remover posibles caracteres problemáticos
            cleaned = response_text
            
            # Corregir comillas mal balanceadas
            cleaned = re.sub(r'"\s*,\s*"(?!:)', '", "', cleaned)
            
            # Corregir llaves dobles {{
            cleaned = re.sub(r'\{\{', '{', cleaned)
            cleaned = re.sub(r'\}\}', '}', cleaned)
            
            # Corregir errores como {"id": "c" ,"d"
            cleaned = re.sub(r'"id":\s*"([a-d])"\s*,\s*"([a-d])"', r'"id": "\1", "text": "opción \1"', cleaned)
            
            # Corregir falta de : después de campos
            cleaned = re.sub(r'"(\w+)"\s*(["{])', r'"\1": \2', cleaned)
            
            # Intentar parsear
            return json.loads(cleaned)
        except:
            pass
        
        # Si es para examen, generar estructura de ejemplo
        if expected_structure == "questions":
            return self._generate_fallback_questions()
        
        # Para otros casos, lanzar excepción
        raise ValueError("No se pudo parsear la respuesta JSON")
    
    def _generate_fallback_questions(self) -> Dict:
        """Genera preguntas de ejemplo cuando falla la generación"""
        return {
            "questions": [
                {
                    "text": "¿Cuál es la función principal de la ALU?",
                    "options": [
                        {"id": "a", "text": "Realizar operaciones aritméticas y lógicas"},
                        {"id": "b", "text": "Almacenar datos temporalmente"},
                        {"id": "c", "text": "Controlar el flujo de instrucciones"},
                        {"id": "d", "text": "Gestionar la memoria cache"}
                    ],
                    "correct_answer": "a",
                    "explanation": "La ALU (Arithmetic Logic Unit) es responsable de realizar todas las operaciones aritméticas y lógicas en el procesador.",
                    "topic": "CPU",
                    "difficulty": "easy"
                }
            ]
        }
            
    async def generate_chat_response(
        self, 
        query: str, 
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Genera una respuesta educativa para consultas sobre arquitectura de computadoras.
        """
        # Si está en modo knowledge_base y no hay contexto, advertir
        if self.processing_mode == ProcessingMode.KNOWLEDGE_BASE and not context:
            return "No hay documentos cargados en la base de conocimiento. Por favor, carga documentos PDF o cambia al modo libre."
        
        # Construir el prompt según el modo
        if self.processing_mode == ProcessingMode.KNOWLEDGE_BASE:
            prompt = self._build_knowledge_base_prompt(query, context, history)
        else:
            prompt = self._build_chat_prompt(query, context, history)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {str(e)}")
            raise

    def _build_knowledge_base_prompt(
        self, 
        query: str, 
        context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Construye prompt para modo base de conocimiento"""
        prompt = f"""Eres un profesor experto en arquitectura de computadoras.
        MODO: BASE DE CONOCIMIENTO
        
        IMPORTANTE: Debes responder ÚNICAMENTE basándote en la siguiente información:
        
        === CONTENIDO DE DOCUMENTOS ===
        {context}
        === FIN DE DOCUMENTOS ===
        
        Reglas estrictas:
        1. Solo usa información que esté explícitamente en los documentos anteriores
        2. Si la información no está en los documentos, di: "Esta información no se encuentra en los documentos disponibles"
        3. NO inventes información ni uses conocimiento externo
        4. Cita las secciones relevantes cuando respondas
        
        Historial de conversación:
        {self._format_history(history) if history else "Sin historial"}
        
        Pregunta del estudiante: {query}
        """
        return prompt
    
    async def generate_exam_questions(
        self, 
        topic: str, 
        difficulty: str,
        num_questions: int,
        subtopics: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> List[Dict]:
        """
        Genera preguntas de opción múltiple para un examen.
        
        Returns:
            Lista de preguntas con formato específico
        """
        logger.info(f"Generando examen - Modo: {self.processing_mode.value}")
        logger.info(f"Contexto disponible: {'SÍ' if context else 'NO'} ({len(context) if context else 0} caracteres)")
        
        if self.processing_mode == ProcessingMode.KNOWLEDGE_BASE:
            if not context:
                logger.warning("KNOWLEDGE_BASE sin contexto - usando preguntas genéricas")
                return self._generate_fallback_questions_for_topic(topic, difficulty, num_questions)
            
            logger.info("Generando preguntas basadas en documentos PDF")
            prompt = self._build_exam_prompt_knowledge_base(topic, difficulty, num_questions, subtopics, context)
        else:
            logger.info("Generando preguntas en modo LIBRE")
            prompt = self._build_exam_prompt(topic, difficulty, num_questions, subtopics)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                print(f"Respuesta recibida: {response.text[:300]}...")  # Mostrar solo los primeros 100 caracteres
                # Usar la función de limpieza
                questions_data = self._clean_json_response(response.text, "questions")
                
                # Validar estructura básica
                if "questions" in questions_data and isinstance(questions_data["questions"], list):
                    # Validar cada pregunta
                    valid_questions = []
                    for q in questions_data["questions"]:
                        if self._validate_question_structure(q):
                            valid_questions.append(q)
                    
                    # Si tenemos al menos una pregunta válida
                    if valid_questions:
                        # Completar con preguntas si faltan
                        while len(valid_questions) < num_questions:
                            valid_questions.append(self._generate_single_fallback_question(topic, difficulty))
                        
                        return valid_questions[:num_questions]
                
            except Exception as e:
                logger.warning(f"Intento {attempt + 1} falló: {str(e)}")
                if attempt < max_retries - 1:
                    # Agregar instrucción adicional al prompt
                    prompt += "\n\nRECUERDA: El JSON debe ser válido. Verifica que todas las llaves estén correctamente cerradas."
                continue
        
        # Si todos los intentos fallan, generar preguntas de respaldo
        logger.error("Todos los intentos de generar preguntas fallaron. Usando preguntas de respaldo.")
        return self._generate_fallback_questions_for_topic(topic, difficulty, num_questions)

    def _build_exam_prompt_knowledge_base(
        self, 
        topic: str, 
        difficulty: str,
        num_questions: int,
        subtopics: Optional[List[str]],
        context: str
    ) -> str:
        """Construye prompt para examen basado en documentos"""
        subtopics_str = ", ".join(subtopics) if subtopics else "todos los aspectos relevantes"
        
        prompt = f"""Genera {num_questions} preguntas de opción múltiple sobre {topic}.
        
        MODO: BASE DE CONOCIMIENTO
        Debes crear las preguntas ÚNICAMENTE basándote en esta información:
        
        === CONTENIDO DE DOCUMENTOS ===
        {context[:5000]}  # Limitar para no exceder límites del modelo
        === FIN DE DOCUMENTOS ===
        
        Nivel de dificultad: {difficulty}
        Subtemas a cubrir: {subtopics_str}
        
        IMPORTANTE: 
        - Las preguntas deben estar basadas SOLO en la información de los documentos
        - No inventes información que no esté en los documentos
        - Responde con el JSON en el formato especificado
        
        Formato JSON requerido:
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
                    "explanation": "explicación basada en los documentos",
                    "topic": "subtema específico",
                    "difficulty": "{difficulty}"
                }}
            ]
        }}
        """
        return prompt

    def _validate_question_structure(self, question: Dict) -> bool:
        """Valida que una pregunta tenga la estructura correcta"""
        required_fields = ["text", "options", "correct_answer", "explanation"]
        
        # Verificar campos requeridos
        for field in required_fields:
            if field not in question:
                return False
        
        # Verificar opciones
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            return False
        
        # Verificar estructura de cada opción
        for opt in question["options"]:
            if not isinstance(opt, dict) or "id" not in opt or "text" not in opt:
                return False
            if opt["id"] not in ["a", "b", "c", "d"]:
                return False
        
        # Verificar respuesta correcta
        if question["correct_answer"] not in ["a", "b", "c", "d"]:
            return False
        
        return True

    def _generate_single_fallback_question(self, topic: str, difficulty: str) -> Dict:
        """Genera una pregunta de respaldo individual"""
        questions_db = {
            "easy": {
                "¿Qué es la memoria cache?": {
                    "correct": "a",
                    "options": {
                        "a": "Memoria de alta velocidad entre CPU y RAM",
                        "b": "Memoria principal del sistema",
                        "c": "Memoria de solo lectura",
                        "d": "Memoria virtual del disco"
                    },
                    "explanation": "La cache es memoria de alta velocidad que almacena datos frecuentemente usados."
                }
            },
            "medium": {
                "¿Cuál es la diferencia principal entre RISC y CISC?": {
                    "correct": "b",
                    "options": {
                        "a": "RISC tiene más registros",
                        "b": "RISC tiene instrucciones simples, CISC complejas",
                        "c": "CISC es más moderno",
                        "d": "No hay diferencia significativa"
                    },
                    "explanation": "RISC usa instrucciones simples y uniformes, mientras CISC tiene instrucciones complejas que pueden hacer múltiples operaciones."
                }
            },
            "hard": {
                "¿Qué técnica usa el pipeline para manejar dependencias de datos?": {
                    "correct": "c",
                    "options": {
                        "a": "Branch prediction",
                        "b": "Cache coherence",
                        "c": "Forwarding o bypassing",
                        "d": "Virtual memory"
                    },
                    "explanation": "Forwarding permite usar resultados de una etapa directamente en otra sin esperar a que se escriban en registros."
                }
            }
        }
        
        # Seleccionar una pregunta del nivel apropiado
        level_questions = questions_db.get(difficulty, questions_db["medium"])
        question_text, data = list(level_questions.items())[0]
        
        return {
            "text": question_text,
            "options": [
                {"id": opt_id, "text": opt_text}
                for opt_id, opt_text in data["options"].items()
            ],
            "correct_answer": data["correct"],
            "explanation": data["explanation"],
            "topic": topic,
            "difficulty": difficulty
        }

    def _generate_fallback_questions_for_topic(self, topic: str, difficulty: str, num_questions: int) -> List[Dict]:
        """Genera múltiples preguntas de respaldo para un tema"""
        questions = []
        for i in range(num_questions):
            question = self._generate_single_fallback_question(topic, difficulty)
            # Variar un poco las preguntas
            question["text"] = f"{question['text']} (Pregunta {i+1})"
            questions.append(question)
        return questions
    
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
        1. Sea técnicamente precisa y consisa  maximo 200 palabras
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
        
        prompt = f"""Genera {num_questions} preguntas  de opción múltiple sobre {topic} ,teniendo de base la 
         arquitectura de computadoras,
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
        3. Cubran diferentes aspectos del tema ,solo y unicamente de arquitectura de computadoras
        4. Las preguntas sean claras y concisas
        5. Sean apropiadas para el nivel de dificultad
        6. Que siempre sea un json válido
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
        