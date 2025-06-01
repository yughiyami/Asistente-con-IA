"""
Servicio de integración con el modelo de lenguaje Google Gemini.
Gestiona las solicitudes al modelo LLM y procesa las respuestas.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple , Union
from datetime import datetime
import google.generativeai as genai

from app.config import settings

# Configurar logger
logger = logging.getLogger(__name__)

# Configurar la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class LLMService:
    """
    Servicio para interactuar con el modelo de lenguaje Google Gemini.
    
    Esta clase proporciona métodos para enviar solicitudes al API de Gemini
    y procesar las respuestas para diferentes casos de uso.
    """
    
    def __init__(self):
        """Inicializa el servicio LLM con la configuración global."""
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite',system_instruction=settings.SYSTEM_PROMPT)
        self.chat_sessions = {}
    
    async def generate_text(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera texto usando el modelo Gemini.
        
        Args:
            prompt: Texto del prompt principal
            context: Texto de contexto adicional (opcional)
            generation_config: Configuración personalizada para la generación (opcional)
            
        Returns:
            El texto generado como respuesta
            
        Raises:
            Exception: Si hay un error en la comunicación con la API
        """
        try:
            # Preparar el prompt con contexto si es necesario
            full_prompt = prompt
            if context:
                full_prompt = f"{prompt}\n\nContexto adicional:\n{context}"
            
            # Configurar la generación
            config = generation_config or {
                "temperature": settings.LLM_TEMPERATURE,
                "top_p": settings.LLM_TOP_P,
                "top_k": settings.LLM_TOP_K,
                "max_output_tokens": settings.LLM_MAX_OUTPUT_TOKENS,
            }
            
            # Generar respuesta
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error al llamar a Gemini: {str(e)}")
            raise
    
    async def get_chat_response(
        self, 
        message: str, 
        session_id: str,
        mode: str = "chat"
    ) -> Dict[str, Any]:
        """
        Obtiene respuesta del modelo para un mensaje en modo conversacional.
        
        Args:
            message: Mensaje o consulta del usuario
            session_id: Identificador único de la conversación
            mode: Modo de respuesta ("chat", "exam", "game", etc.)
            
        Returns:
            Diccionario con texto de respuesta y consultas de imágenes sugeridas
        """
        try:
            # Crear nueva sesión si no existe
            if session_id not in self.chat_sessions:
                self.chat_sessions[session_id] = self.model.start_chat(
                    enable_automatic_function_calling=True
                )
            
            # Ajustar prompt según modo
            if mode == "chat":
                prompt = f"Responde a esta pregunta sobre arquitectura de computadoras: {message}. Si es relevante, indica qué imágenes serían útiles incluir, marcándolas con IMAGEN_SUGERIDA: [descripción]."
            else:
                prompt = message
            
            # Obtener respuesta
            chat = self.chat_sessions[session_id]
            logger.debug(f"Historial de chat: {chat.history}")
            response = await chat.send_message_async(prompt)
            
            text_response = response.text
            
            # Extraer sugerencias de imágenes
            images = []
            if "IMAGEN_SUGERIDA:" in text_response:
                # Extraer sugerencias de imágenes y eliminarlas del texto
                image_suggestions = re.findall(r'IMAGEN_SUGERIDA: \[(.*?)\]', text_response)
                text_response = re.sub(r'IMAGEN_SUGERIDA: \[(.*?)\]', '', text_response).strip()
                
                # Convertir sugerencias en información de imágenes
                for suggestion in image_suggestions:
                    images.append({
                        "description": suggestion,
                        "query": f"computer architecture {suggestion}"
                    })
            
            return {
                "text": text_response,
                "image_queries": images
            }
            
        except Exception as e:
            logger.error(f"Error en get_chat_response: {str(e)}")
            return {
                "text": f"Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta de nuevo.",
                "image_queries": []
            }
    
    async def generate_json(
        self, 
        prompt: str, 
        expected_structure: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera una respuesta en formato JSON.
        
        Args:
            prompt: Texto del prompt principal
            expected_structure: Estructura esperada del JSON (para incluirla en el prompt)
            context: Texto de contexto adicional (opcional)
            
        Returns:
            Diccionario con la respuesta en formato JSON
            
        Raises:
            ValueError: Si la respuesta no se puede parsear como JSON válido
        """
        # Agregar instrucciones para formato JSON
        json_prompt = f"""
{prompt}

Responde SOLAMENTE con un objeto JSON válido con la siguiente estructura:
{json.dumps(expected_structure, indent=2)}

Tu respuesta debe ser un JSON válido y nada más. No incluyas texto adicional, comillas triples,
ni la palabra "json" antes o después del objeto JSON.
"""
        
        try:
            response = await self.model.generate_content_async(
                json_prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": settings.LLM_MAX_OUTPUT_TOKENS,
                }
            )
            
            # Extraer JSON de la respuesta
            text_response = response.text
            
            # Buscar JSON en la respuesta
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text_response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'(\{[\s\S]*\})', text_response)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    raise ValueError("No se pudo extraer JSON de la respuesta")
            
            # Parsear JSON
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {str(e)}")
            logger.error(f"Respuesta recibida: {text_response}")
            raise ValueError(f"La respuesta no es un JSON válido: {str(e)}")
    
    async def generate_exam(
        self, 
        topic: str, 
        difficulty: str = "medium", 
        question_count: int = 10
    ) -> Dict[str, Any]:
        """
        Genera un examen con preguntas de opción múltiple y respuesta abierta.
        
        Args:
            topic: Tema del examen
            difficulty: Nivel de dificultad ("easy", "medium", "hard")
            question_count: Número de preguntas a generar
            
        Returns:
            Diccionario con la estructura del examen
        """
        prompt = f"""
        Crea un examen de arquitectura de computadoras sobre el tema: {topic}.
        Dificultad: {difficulty}
        Genera exactamente {question_count} preguntas en total:
        - 7 preguntas de opción múltiple, cada una con 4 opciones
        - 3 preguntas de respuesta abierta
        
        Formatea el resultado como un JSON con esta estructura:
        {{
          "title": "Título del examen",
          "description": "Descripción breve",
          "questions": [
            {{
              "question_text": "Texto de la pregunta",
              "question_type": "multiple_choice",
              "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
              "correct_answer": "0", // Índice de la opción correcta (0-based)
              "explanation": "Explicación de la respuesta correcta",
              "points": 1
            }},
            {{
              "question_text": "Texto de la pregunta abierta",
              "question_type": "open_ended",
              "correct_answer": "Respuesta esperada simplificada",
              "explanation": "Explicación completa",
              "points": 3
            }}
          ]
        }}
        
        Asegúrate de que las preguntas sean claras, precisas y relevantes para el tema.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 4096,
                }
            )
            
            # Extraer JSON de la respuesta
            text_response = response.text
            
            # Buscar JSON en la respuesta
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text_response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'(\{[\s\S]*\})', text_response)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    raise ValueError("No se pudo extraer JSON de la respuesta")
            
            # Parsear JSON
            exam_data = json.loads(json_str)
            return exam_data
            
        except Exception as e:
            logger.error(f"Error en generate_exam: {str(e)}")
            return {
                "title": f"Examen sobre {topic}",
                "description": "Se produjo un error al generar el examen",
                "questions": []
            }
    
    async def evaluate_exam(
        self, 
        exam_data: Dict[str, Any], 
        user_answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evalúa las respuestas del examen y proporciona retroalimentación.
        
        Args:
            exam_data: Datos del examen
            user_answers: Respuestas proporcionadas por el usuario
            
        Returns:
            Resultado de la evaluación con puntuación y feedback
        """
        questions = exam_data.get("questions", [])
        total_points = sum(q.get("points", 1) for q in questions)
        score = 0
        results = []
        
        for question in questions:
            question_id = question.get("id", "")
            if question_id not in user_answers:
                # Pregunta sin responder
                results.append({
                    "question_id": question_id,
                    "correct": False,
                    "points_earned": 0,
                    "points_possible": question.get("points", 1),
                    "correct_answer": question.get("correct_answer"),
                    "explanation": question.get("explanation", "")
                })
                continue
            
            user_answer = user_answers[question_id]
            question_type = question.get("question_type")
            
            if question_type == "multiple_choice":
                # Convertir a string para comparación
                correct = str(user_answer) == str(question.get("correct_answer"))
                points_earned = question.get("points", 1) if correct else 0
                score += points_earned
                
                results.append({
                    "question_id": question_id,
                    "correct": correct,
                    "points_earned": points_earned,
                    "points_possible": question.get("points", 1),
                    "user_answer": user_answer,
                    "correct_answer": question.get("correct_answer"),
                    "explanation": question.get("explanation", "")
                })
            elif question_type == "open_ended":
                # Para preguntas abiertas, evaluamos con el modelo
                eval_prompt = f"""
                Evalúa la siguiente respuesta a una pregunta abierta sobre arquitectura de computadoras:
                
                Pregunta: {question.get("question_text")}
                Respuesta esperada: {question.get("correct_answer")}
                Respuesta del estudiante: {user_answer}
                
                Evalúa la precisión y completitud de la respuesta en una escala de 0-100%. 
                Devuelve solo el porcentaje como un número entero, sin texto adicional.
                """
                
                try:
                    eval_response = await self.model.generate_content_async(
                        eval_prompt,
                        generation_config={"temperature": 0.1}
                    )
                    
                    # Extraer porcentaje
                    score_match = re.search(r'(\d{1,3})%?', eval_response.text)
                    if score_match:
                        accuracy = int(score_match.group(1)) / 100
                    else:
                        accuracy = 0.5  # Default if no match
                    
                    points_possible = question.get("points", 3)
                    points_earned = round(accuracy * points_possible, 1)
                    score += points_earned
                    
                    results.append({
                        "question_id": question_id,
                        "correct": accuracy >= 0.7,  # Consider "correct" if >= 70%
                        "points_earned": points_earned,
                        "points_possible": points_possible,
                        "accuracy": accuracy,
                        "user_answer": user_answer,
                        "expected_answer": question.get("correct_answer"),
                        "explanation": question.get("explanation", "")
                    })
                except Exception as e:
                    logger.error(f"Error evaluando pregunta abierta: {str(e)}")
                    # Asignar puntuación predeterminada
                    points_possible = question.get("points", 3)
                    points_earned = points_possible / 2  # 50% by default on error
                    score += points_earned
                    results.append({
                        "question_id": question_id,
                        "correct": None,  # Unknown correctness
                        "points_earned": points_earned,
                        "points_possible": points_possible,
                        "user_answer": user_answer,
                        "error": "Error en la evaluación",
                        "explanation": question.get("explanation", "")
                    })
        
        # Calcular porcentaje
        percentage = (score / total_points) * 100 if total_points > 0 else 0
        
        # Generar retroalimentación general
        feedback_prompt = f"""
        Un estudiante ha completado un examen sobre {exam_data.get("title")} con {score:.1f} puntos de {total_points} ({percentage:.1f}%).
        Proporciona una retroalimentación educativa que:
        1. Reconozca su esfuerzo
        2. Destaque aspectos positivos
        3. Sugiera áreas de mejora basadas en los resultados
        4. Ofrezca recomendaciones de estudio

        Mantén la retroalimentación concisa (máximo 3-4 oraciones) y motivadora.
        """
        
        try:
            feedback_response = await self.model.generate_content_async(
                feedback_prompt,
                generation_config={"temperature": 0.7}
            )
            feedback = feedback_response.text.strip()
        except Exception:
            feedback = f"Has obtenido {score:.1f} de {total_points} puntos ({percentage:.1f}%). Revisa las explicaciones de cada pregunta para mejorar tu comprensión."
        
        return {
            "score": score,
            "total_points": total_points,
            "percentage": percentage,
            "question_results": results,
            "feedback": feedback
        }
    
    async def extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extrae un objeto JSON de un texto que puede contener información adicional.
        
        Args:
            text: Texto que contiene un objeto JSON
            
        Returns:
            Diccionario con el JSON extraído
            
        Raises:
            ValueError: Si no se puede encontrar o parsear un JSON válido
        """
        # Intenta encontrar un objeto JSON en el texto
        
        # Primero, busca un bloque de código JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Si no hay bloques de código, busca un patrón JSON
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
            json_match = re.search(json_pattern, text)
            
            if not json_match:
                raise ValueError("No se pudo encontrar un objeto JSON en el texto proporcionado")
            
            json_str = json_match.group(0)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Se encontró un posible JSON pero no es válido: {str(e)}")
    
    async def initialize_game(
        self, 
        game_type: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inicializa un juego educativo del tipo especificado.
        
        Args:
            game_type: Tipo de juego a inicializar
            config: Configuración opcional para el juego
            
        Returns:
            Estado inicial del juego
        """
        # Implementación basada en el código original
        game_state = {}
        config = config or {}
        
        if game_type == "hangman":
            # Juego del ahorcado
            from random import choice
            word_list = settings.GAMES_CONFIG.get("hangman", {}).get("word_list", [])
            selected_word = choice(word_list) if word_list else "PROCESADOR"
            
            game_state = {
                "type": "hangman",
                "word": selected_word,
                "display": "_" * len(selected_word),
                "guessed_letters": [],
                "wrong_guesses": 0,
                "max_wrong_guesses": 6,
                "completed": False,
                "won": False,
                "category": "Arquitectura de Computadoras",
                "hint": self._get_hangman_hint(selected_word),
                "instructions": "Adivina la palabra relacionada con arquitectura de computadoras "
                               "antes de completar el ahorcado."
            }
            
        elif game_type == "wordle":
            # Implementación similar al juego de wordle
            from random import choice
            words = ["CACHE", "STACK", "BUSES", "CLOCK", "RISC"]
            selected_word = choice(words)
            
            game_state = {
                "type": "wordle",
                "word": selected_word,
                "display": "_" * len(selected_word),
                "attempts": [],
                "results": [],
                "max_attempts": 6,
                "completed": False,
                "won": False,
                "hint": f"Término de 5 letras relacionado con arquitectura de computadoras",
                "instructions": "Adivina la palabra de 5 letras. Después de cada intento, "
                               "verás qué letras están en la posición correcta, "
                               "cuáles están en la palabra pero en otra posición, "
                               "y cuáles no están en la palabra."
            }
            
        elif game_type == "logic_diagram":
            # Implementación básica para diagramas lógicos
            game_state = {
                "type": "logic_diagram",
                "components": ["AND", "OR", "NOT", "XOR", "NAND", "NOR"],
                "current_challenge": {
                    "description": "Implementa un circuito que muestre '1' solo cuando exactamente una entrada es '1'",
                    "inputs": 2,
                    "expected_outputs": [[0,0,0], [0,1,1], [1,0,1], [1,1,0]],  # [A,B,Out]
                    "hint": "Piensa en una función XOR"
                },
                "score": 0,
                "completed": False,
                "instructions": "Construye circuitos lógicos para implementar la función especificada "
                               "utilizando las compuertas disponibles."
            }
            
        elif game_type == "assembler":
            # Implementación para ejercicios de ensamblador
            game_state = {
                "type": "assembler",
                "architecture": "MIPS",
                "registers": {"$zero": 0, "$at": 0, "$v0": 0, "$v1": 0, "$a0": 0, "$a1": 0},
                "memory": {},
                "pc": 0,
                "current_challenge": {
                    "description": "Escribe un programa en MIPS que sume los valores de $t0 y $t1 y guarde el resultado en $t2",
                    "initial_state": {"$t0": 5, "$t1": 7},
                    "expected_result": {"$t2": 12},
                    "hint": "Usa la instrucción add"
                },
                "completed": False,
                "instructions": "Escribe código en lenguaje ensamblador MIPS para resolver problemas simples."
            }
            
        return game_state
    
    async def process_game_action(
        self, 
        game_state: Dict[str, Any], 
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Procesa una acción en un juego y actualiza el estado.
        
        Args:
            game_state: Estado actual del juego
            action: Acción a realizar
            
        Returns:
            Estado actualizado y mensaje
        """
        game_type = game_state.get("type", "")
        action_type = action.get("action", "")
        action_data = action.get("data", {})
        
        # Copia del estado actual para modificar
        new_state = game_state.copy()
        message = None
        
        # Procesar acción según el tipo de juego
        if game_type == "hangman":
            if action_type == "guess_letter":
                letter = action_data.get("letter", "").upper()
                
                if letter and len(letter) == 1 and letter not in new_state["guessed_letters"]:
                    # Procesar la letra adivinada
                    new_state["guessed_letters"].append(letter)
                    
                    if letter in new_state["word"]:
                        # Actualizar display
                        word = new_state["word"]
                        display = list(new_state["display"])
                        
                        for i in range(len(word)):
                            if word[i] == letter:
                                display[i] = letter
                        
                        new_state["display"] = "".join(display)
                        message = f"¡Bien! La letra '{letter}' está en la palabra."
                        
                        # Verificar si ganó
                        if "_" not in new_state["display"]:
                            new_state["completed"] = True
                            new_state["won"] = True
                            message = f"¡Felicidades! Has adivinado la palabra: {new_state['word']}"
                    else:
                        new_state["wrong_guesses"] += 1
                        message = f"La letra '{letter}' no está en la palabra."
                        
                        # Verificar si perdió
                        if new_state["wrong_guesses"] >= new_state["max_wrong_guesses"]:
                            new_state["completed"] = True
                            message = f"¡Oh no! Te has quedado sin intentos. La palabra era: {new_state['word']}"
            
            elif action_type == "guess_word":
                guess = action_data.get("word", "").upper()
                
                if guess:
                    if guess == new_state["word"]:
                        new_state["display"] = new_state["word"]
                        new_state["completed"] = True
                        new_state["won"] = True
                        message = f"¡Felicidades! Has adivinado la palabra: {new_state['word']}"
                    else:
                        new_state["wrong_guesses"] += 2  # Penalización por intentar adivinar la palabra completa
                        message = f"Incorrecto. '{guess}' no es la palabra correcta."
                        
                        # Verificar si perdió
                        if new_state["wrong_guesses"] >= new_state["max_wrong_guesses"]:
                            new_state["completed"] = True
                            message = f"¡Oh no! Te has quedado sin intentos. La palabra era: {new_state['word']}"
                            
        # Procesamiento básico para wordle (similar a hangman pero con lógica específica)
        elif game_type == "wordle":
            if action_type == "guess_word":
                guess = action_data.get("word", "").upper()
                
                if guess and len(guess) == 5:
                    # Registrar intento
                    new_state["attempts"].append(guess)
                    
                    # Calcular resultado
                    word = new_state["word"]
                    result = []
                    
                    # Primero, marcar letras correctas en posición correcta
                    word_chars = list(word)
                    for i, char in enumerate(guess):
                        if i < len(word) and char == word[i]:
                            result.append("correct")
                            word_chars[i] = "*"  # Marcar como usada
                        else:
                            result.append(None)  # Temporal
                    
                    # Luego, marcar letras presentes pero en posición incorrecta
                    for i, char in enumerate(guess):
                        if result[i] is None:  # Solo procesar posiciones aún sin resultado
                            if char in word_chars:
                                result[i] = "present"
                                word_chars[word_chars.index(char)] = "*"  # Marcar como usada
                            else:
                                result[i] = "absent"
                    
                    new_state["results"].append(result)
                    
                    # Verificar si ganó
                    if guess == word:
                        new_state["completed"] = True
                        new_state["won"] = True
                        message = f"¡Felicidades! Has adivinado la palabra: {word}"
                    elif len(new_state["attempts"]) >= new_state["max_attempts"]:
                        new_state["completed"] = True
                        message = f"Se acabaron los intentos. La palabra era: {word}"
                    else:
                        attempt_num = len(new_state["attempts"])
                        message = f"Intento {attempt_num}/{new_state['max_attempts']}"
        
        # Otros juegos podrían implementarse siguiendo patrones similares
        
        return {
            "state": new_state,
            "message": message
        }
    
    def _get_hangman_hint(self, word: str) -> str:
        """Genera una pista para el juego del ahorcado."""
        hints = {
            "PROCESADOR": "Componente central que ejecuta instrucciones",
            "MEMORIA": "Almacena datos e instrucciones temporalmente",
            "REGISTRO": "Pequeña unidad de almacenamiento dentro del CPU",
            "CACHE": "Memoria rápida que guarda datos frecuentemente usados",
            "PIPELINE": "Técnica para ejecutar múltiples instrucciones simultáneamente",
            "ARQUITECTURA": "Diseño y estructura fundamental de un sistema",
            "ENSAMBLADOR": "Lenguaje de programación de bajo nivel",
            "INTERRUPCIONES": "Señales que detienen temporalmente la ejecución",
            "DIRECCIONAMIENTO": "Método para identificar ubicaciones de memoria",
            "MICROPROCESADOR": "Circuito integrado que actúa como unidad central",
            "FIRMWARE": "Software permanente programado en un hardware",
            "MICROCONTROLADOR": "Chip que integra CPU, memoria y periféricos"
        }
        
        return hints.get(word, "Un concepto de arquitectura de computadoras")
    def _get_improved_system_prompt(self) -> str:
        """Genera un prompt de sistema mejorado para juegos educativos."""
        return """
        Eres un asistente especializado en crear contenido educativo para arquitectura de computadoras.

        REGLAS CRÍTICAS:
        1. NUNCA uses respuestas genéricas o por defecto
        2. TODAS las respuestas deben limitarse a 100 palabras MÁXIMO
        3. Sé específico y técnicamente preciso
        4. Enfócate en conceptos de arquitectura de computadoras
        5. Adapta la dificultad al nivel solicitado
        6. Proporciona contenido original y educativo

        ESPECIALIDADES:
        - Procesadores y microarquitectura
        - Sistemas de memoria y cache
        - Entrada/salida y buses
        - Lenguaje ensamblador
        - Lógica digital y compuertas

        FORMATO DE RESPUESTAS:
        - Conciso pero informativo
        - Técnicamente correcto
        - Educativamente valioso
        - Sin información irrelevante
        """
    
    async def generate_hangman_word(
        self, 
        difficulty: str, 
        topic: str, 
        word_length_range: Tuple[int, int]
    ) -> Dict[str, str]:
        """
        Genera una palabra específica para el juego de ahorcado.
        
        Args:
            difficulty: Nivel de dificultad
            topic: Tema específico
            word_length_range: Rango de longitud de palabra
            
        Returns:
            Diccionario con palabra, pista y explicación
        """
        min_len, max_len = word_length_range
        
        prompt = f"""
        Genera UNA palabra técnica para ahorcado en arquitectura de computadoras.
        
        ESPECIFICACIONES:
        - Tema: {topic}
        - Dificultad: {difficulty}
        - Longitud: {min_len}-{max_len} caracteres
        - Solo letras, sin espacios ni guiones
        
        RESPUESTA MÁXIMO 100 PALABRAS.
        
        JSON esperado:
        {{
          "word": "PALABRA_EXACTA",
          "clue": "Pista específica (máximo 30 palabras)",
          "argument": "Explicación técnica (máximo 40 palabras)"
        }}
        
        EVITA respuestas genéricas. Sé específico sobre {topic}.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_output_tokens": 300
                }
            )
            
            # Extraer y validar JSON
            result = await self.extract_json_from_text(response.text)
            
            # Validaciones específicas
            word = result.get("word", "").upper()
            if not word or not word.isalpha() or len(word) < min_len or len(word) > max_len:
                raise ValueError("Palabra no válida generada")
            
            return {
                "word": word,
                "clue": result.get("clue", "")[:100],  # Limitar clue
                "argument": result.get("argument", "")[:100]  # Limitar explicación
            }
            
        except Exception as e:
            logger.error(f"Error generando palabra para ahorcado: {str(e)}")
            # Respuesta de respaldo específica
            return self._get_fallback_hangman_word(difficulty, topic, word_length_range)
    


    

    async def _generate_simple_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Genera circuito simple para nivel easy - MEJORADO CON DIVERSIDAD."""
        
        # Patrones educativos específicos para easy
        educational_patterns = [
            "detector de entradas iguales",
            "selector de mayoría simple", 
            "inversor condicional",
            "puerta de activación dual",
            "filtro de señales básico"
        ]
        
        import random
        selected_pattern = random.choice(educational_patterns)
        
        prompt = f"""
        Diseña un circuito lógico EDUCATIVO específico para estudiantes.
        
        ESPECIFICACIONES OBLIGATORIAS:
        - Propósito: {selected_pattern}
        - Compuertas: {gates_count} (USAR TIPOS DIFERENTES)
        - Entradas iniciales: {inputs_count}
        - Resultado: DEBE ser educativo y demostrar un concepto específico
        
        VARIEDAD OBLIGATORIA:
        - NO uses solo AND/OR básicas
        - Incluye compuertas como XOR, NAND, NOR según el propósito
        - Entradas deben demostrar diferentes comportamientos
        - Salida debe ser 0 O 1 (no siempre 1)
        
        RESPUESTA MÁXIMO 80 PALABRAS.
        
        JSON esperado:
        {{
          "pattern": ["NAND", "XOR"],
          "input_values": [
            [1, 1, 0],
            [0, 1, 1]
          ],
          "expected_output": 1,
          "complexity_type": "single_output",
          "description": "Descripción técnica específica del propósito"
        }}
        
        IMPORTANTE: Crea un circuito que demuestre un concepto específico de lógica digital.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.7,  # Aumentar creatividad
                    "top_p": 0.9,
                    "top_k": 50,
                    "max_output_tokens": 400
                }
            )
            
            result = await self.extract_json_from_text(response.text)
            result["complexity_type"] = "single_output"
            
            # Validar diversidad
            pattern = result.get("pattern", [])
            if len(set(pattern)) < max(1, len(pattern) - 1):  # Al menos diferentes tipos
                logger.warning("Patrón poco diverso, usando fallback variado")
                return self._get_diverse_fallback_simple(difficulty, gates_count, inputs_count)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando circuito simple diverso: {str(e)}")
            return self._get_diverse_fallback_simple(difficulty, gates_count, inputs_count)
    
    async def _generate_multiple_cases_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int,
        cases_count: int
    ) -> Dict[str, Any]:
        """Genera circuito con múltiples casos para nivel medium - DIVERSIDAD MEJORADA."""
        
        # Conceptos educativos específicos para medium
        advanced_concepts = [
            "decodificador de 2 bits",
            "comparador de magnitud",
            "detector de paridad par/impar", 
            "multiplexor básico 2:1",
            "generador de código Gray",
            "detector de secuencia específica"
        ]
        
        import random
        selected_concept = random.choice(advanced_concepts)
        
        prompt = f"""
        Diseña un circuito lógico AVANZADO que implemente: {selected_concept}
        
        ESPECIFICACIONES OBLIGATORIAS:
        - Concepto: {selected_concept}
        - Compuertas: {gates_count} (TIPOS VARIADOS obligatorio)
        - Casos de prueba: {cases_count} (ENTRADAS DIFERENTES)
        - Cada caso debe mostrar un comportamiento único del circuito
        
        DIVERSIDAD OBLIGATORIA:
        - Usa compuertas: XOR, NAND, NOR, NOT (no solo AND/OR)
        - Entradas iniciales DIFERENTES para cada caso
        - Salidas VARIADAS (no todas iguales)
        - Demuestra el concepto técnico claramente
        
        RESPUESTA MÁXIMO 120 PALABRAS.
        
        JSON esperado:
        {{
          "pattern": ["XOR", "NAND", "OR"],
          "test_cases": [
            {{
              "case_id": "case1",
              "input_values": [[0, 0, 0], [0, 1, 1], [1, 1, 1]],
              "expected_output": 1
            }},
            {{
              "case_id": "case2", 
              "input_values": [[1, 0, 1], [1, 0, 0], [0, 1, 1]],
              "expected_output": 0
            }},
            {{
              "case_id": "case3",
              "input_values": [[1, 1, 1], [1, 0, 1], [1, 0, 1]], 
              "expected_output": 1
            }}
          ],
          "expected_output": {{"case1": 1, "case2": 0, "case3": 1}},
          "complexity_type": "multiple_cases",
          "description": "Implementación técnica de {selected_concept}"
        }}
        
        CRÍTICO: Las salidas deben ser DIFERENTES para demostrar el concepto. NO todas 1 o todas 0.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.8,  # Alta creatividad
                    "top_p": 0.95,
                    "top_k": 60,
                    "max_output_tokens": 600
                }
            )
            
            result = await self.extract_json_from_text(response.text)
            result["complexity_type"] = "multiple_cases"
            
            # Validar diversidad en las salidas
            expected_output = result.get("expected_output", {})
            if isinstance(expected_output, dict):
                unique_outputs = set(expected_output.values())
                if len(unique_outputs) < 2:  # Al menos 2 salidas diferentes
                    logger.warning("Salidas poco diversas, usando fallback variado")
                    return self._get_diverse_fallback_multiple_cases(difficulty, gates_count, cases_count)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando circuito múltiples casos diverso: {str(e)}")
            return self._get_diverse_fallback_multiple_cases(difficulty, gates_count, cases_count)
    
    async def _generate_pattern_analysis_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Genera circuito con análisis de patrones para nivel hard - COMPLEJIDAD REAL."""
        
        # Patrones complejos para hard
        complex_patterns = [
            "contador binario cíclico",
            "generador de secuencia Fibonacci módulo 2",
            "máquina de estados de 4 estados",
            "detector de palindromo binario",
            "generador de números primos módulo 2",
            "secuencia pseudo-aleatoria simple"
        ]
        
        import random
        selected_pattern = random.choice(complex_patterns)
        
        prompt = f"""
        Diseña un circuito lógico COMPLEJO que implemente: {selected_pattern}
        
        ESPECIFICACIONES AVANZADAS:
        - Sistema: {selected_pattern}
        - Compuertas: {gates_count} (MÁXIMA VARIEDAD)
        - Debe generar una secuencia de 8 valores que demuestre el patrón
        - Análisis requerido: patrón, ciclo, estado final
        
        COMPLEJIDAD OBLIGATORIA:
        - Usa todas las compuertas: XOR, NAND, NOR, NOT, AND, OR
        - Secuencia debe mostrar un patrón matemático/lógico real
        - Ciclo debe ser detectable (longitud 2, 3, 4, etc.)
        - Estado final debe ser calculable
        
        RESPUESTA MÁXIMO 150 PALABRAS.
        
        JSON esperado:
        {{
          "pattern": ["XOR", "NAND", "NOR", "NOT"],
          "sequence_inputs": [
            [1, 0], [0, 1], [1, 1], [0, 0], [1, 0], [0, 1], [1, 1], [0, 0]
          ],
          "pattern_analysis": {{
            "sequence": [1, 0, 0, 1, 1, 0, 0, 1],
            "pattern_type": "repeating",
            "cycle_length": 4,
            "final_state": 1,
            "frequency": {{"0": 4, "1": 4}}
          }},
          "expected_output": {{
            "pattern": [1, 0, 0, 1, 1, 0, 0, 1],
            "final_state": 1,
            "cycle_length": 4
          }},
          "complexity_type": "pattern_analysis",
          "description": "Implementación de {selected_pattern} con análisis matemático"
        }}
        
        OBLIGATORIO: El patrón debe ser matemáticamente coherente y educativo.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.9,  # Máxima creatividad
                    "top_p": 0.95,
                    "top_k": 80,
                    "max_output_tokens": 800
                }
            )
            
            result = await self.extract_json_from_text(response.text)
            result["complexity_type"] = "pattern_analysis"
            
            # Validar complejidad del patrón
            pattern_data = result.get("pattern_analysis", {})
            sequence = pattern_data.get("sequence", [])
            
            if len(set(sequence)) < 2 or len(sequence) < 6:  # Muy simple
                logger.warning("Patrón demasiado simple, usando fallback complejo")
                return self._get_diverse_fallback_pattern_analysis(difficulty, gates_count)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando circuito de análisis complejo: {str(e)}")
            return self._get_diverse_fallback_pattern_analysis(difficulty, gates_count)
    
    # Fallbacks diversos mejorados
    
    def _get_diverse_fallback_simple(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Fallbacks diversos para circuito simple."""
        fallbacks = [
            {
                "pattern": ["NAND", "XOR"],
                "input_values": [[1, 1, 0], [0, 1, 1]],
                "expected_output": 1,
                "description": "Detector NAND-XOR: activo cuando entradas son diferentes después de NAND"
            },
            {
                "pattern": ["NOR", "AND"],
                "input_values": [[0, 1, 0], [0, 0, 0]],
                "expected_output": 0,
                "description": "Filtro NOR-AND: bloquea la mayoría de señales"
            },
            {
                "pattern": ["XOR", "NOT"],
                "input_values": [[1, 0, 1], [1, 0]],
                "expected_output": 0,
                "description": "Inversor XOR: invierte resultado de diferencia"
            }
        ]
        
        import random
        selected = random.choice(fallbacks)
        selected["complexity_type"] = "single_output"
        return selected
    
    def _get_diverse_fallback_multiple_cases(
        self, 
        difficulty: str, 
        gates_count: int, 
        cases_count: int
    ) -> Dict[str, Any]:
        """Fallbacks diversos para múltiples casos."""
        fallbacks = [
            {
                "pattern": ["XOR", "NAND", "OR"],
                "test_cases": [
                    {"case_id": "case1", "input_values": [[0, 1, 1], [1, 0, 0], [0, 1, 1]], "expected_output": 1},
                    {"case_id": "case2", "input_values": [[1, 0, 1], [1, 0, 0], [0, 0, 0]], "expected_output": 0},
                    {"case_id": "case3", "input_values": [[1, 1, 0], [0, 1, 1], [1, 0, 1]], "expected_output": 1}
                ],
                "expected_output": {"case1": 1, "case2": 0, "case3": 1},
                "description": "Detector de paridad complejo con casos variados"
            },
            {
                "pattern": ["NOR", "XOR", "AND"],
                "test_cases": [
                    {"case_id": "case1", "input_values": [[0, 0, 1], [1, 1, 0], [0, 1, 0]], "expected_output": 0},
                    {"case_id": "case2", "input_values": [[1, 1, 0], [0, 0, 0], [0, 1, 0]], "expected_output": 0},
                    {"case_id": "case3", "input_values": [[0, 1, 0], [0, 1, 1], [1, 0, 1]], "expected_output": 1}
                ],
                "expected_output": {"case1": 0, "case2": 0, "case3": 1},
                "description": "Filtro selectivo NOR-XOR-AND con diferentes comportamientos"
            }
        ]
        
        import random
        selected = random.choice(fallbacks)
        selected["complexity_type"] = "multiple_cases"
        return selected
    
    def _get_diverse_fallback_pattern_analysis(
        self, 
        difficulty: str, 
        gates_count: int
    ) -> Dict[str, Any]:
        """Fallbacks diversos para análisis de patrones."""
        fallbacks = [
            {
                "pattern": ["XOR", "NAND", "NOR", "NOT"],
                "sequence_inputs": [[1, 0], [0, 1], [1, 1], [0, 0], [1, 0], [0, 1]],
                "expected_output": {
                    "pattern": [1, 0, 0, 1, 1, 0],
                    "final_state": 0,
                    "cycle_length": 3
                },
                "description": "Contador ternario con secuencia 1-0-0 repetitiva"
            },
            {
                "pattern": ["NAND", "XOR", "OR", "NOT"],
                "sequence_inputs": [[0, 1], [1, 0], [0, 0], [1, 1], [0, 1], [1, 0]],
                "expected_output": {
                    "pattern": [0, 1, 1, 0, 0, 1],
                    "final_state": 1,
                    "cycle_length": 2
                },
                "description": "Generador de paridad alternante con patrón 0-1-1-0"
            }
        ]
        
        import random
        selected = random.choice(fallbacks)
        selected["complexity_type"] = "pattern_analysis"
        return selected
    # Métodos de fallback específicos
    
    def _get_fallback_simple_circuit_new(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Fallback para circuito simple."""
        return {
            "pattern": ["AND", "OR"],
            "input_values": [
                [1, 1, 1],
                [1, 0, 1]
            ],
            "expected_output": 1,
            "complexity_type": "single_output",
            "description": "Circuito AND seguido de OR"
        }
    
    def _get_fallback_multiple_cases_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        cases_count: int
    ) -> Dict[str, Any]:
        """Fallback para múltiples casos."""
        return {
            "pattern": ["AND", "XOR", "OR"],
            "test_cases": [
                {
                    "case_id": "case1",
                    "input_values": [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
                    "expected_output": 1
                },
                {
                    "case_id": "case2",
                    "input_values": [[0, 1, 0], [0, 1, 1], [1, 0, 1]],
                    "expected_output": 1
                },
                {
                    "case_id": "case3",
                    "input_values": [[1, 0, 0], [0, 1, 1], [1, 1, 1]],
                    "expected_output": 1
                }
            ],
            "expected_output": {"case1": 1, "case2": 1, "case3": 1},
            "complexity_type": "multiple_cases",
            "description": "Circuito evaluado con múltiples casos"
        }
    
    def _get_fallback_pattern_analysis_circuit(
        self, 
        difficulty: str, 
        gates_count: int
    ) -> Dict[str, Any]:
        """Fallback para análisis de patrones."""
        return {
            "pattern": ["XOR", "AND", "OR", "NOT"],
            "sequence_inputs": [
                [1, 0], [0, 1], [1, 1], [0, 0]
            ],
            "pattern_analysis": {
                "sequence": [1, 0, 1, 0, 1, 0, 1, 0],
                "pattern_type": "alternating",
                "cycle_length": 2,
                "final_state": 0,
                "frequency": {"0": 4, "1": 4}
            },
            "expected_output": {
                "pattern": [1, 0, 1, 0, 1, 0, 1, 0],
                "final_state": 0,
                "cycle_length": 2
            },
            "complexity_type": "pattern_analysis",
            "description": "Circuito que genera patrón alternante"
        }
    
    async def generate_assembly_exercise(
        self, 
        difficulty: str, 
        architecture: str, 
        error_type: str,
        instructions_count: int
    ) -> Dict[str, str]:
        """
        Genera ejercicio de ensamblador con código errado específico.
        
        Args:
            difficulty: Nivel de dificultad
            architecture: Arquitectura objetivo
            error_type: Tipo de error a incluir
            instructions_count: Número de instrucciones
            
        Returns:
            Código errado con información del error
        """
        prompt = f"""
        Crea código ensamblador CON ERROR ESPECÍFICO para arquitectura de computadoras.
        
        ESPECIFICACIONES:
        - Arquitectura: {architecture}
        - Dificultad: {difficulty}
        - Tipo de error: {error_type}
        - Instrucciones: {instructions_count}
        
        RESPUESTA MÁXIMO 100 PALABRAS.
        
        Crea código que:
        - Tenga un propósito educativo claro
        - Contenga UN error específico del tipo {error_type}
        - Sea realista y educativo
        - No sea genérico ni trivial
        
        JSON esperado:
        {{
          "buggy_code": "código con error específico",
          "expected_behavior": "qué debería hacer (máximo 25 palabras)",
          "hint": "pista específica sobre el error (máximo 20 palabras)",
          "error_explanation": "explicación técnica del error para evaluación"
        }}
        
        EVITA ejemplos triviales. Crea código con propósito educativo real.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_output_tokens": 400
                }
            )
            
            result = await self.extract_json_from_text(response.text)
            
            # Validar que el código no sea trivial
            code = result.get("buggy_code", "")
            if not code or len(code.split('\n')) < 2:
                raise ValueError("Código generado es demasiado simple")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando ejercicio de ensamblador: {str(e)}")
            return self._get_fallback_assembly_exercise(difficulty, architecture, error_type)
    
    async def explain_logic_circuit(
        self, 
        circuit_description: str,
        gates_sequence: List[str],
        test_input: List[int],
        expected_output: int,
        user_answer: int
    ) -> str:
        """
        Genera explicación específica sobre el funcionamiento de un circuito lógico.
        
        Args:
            circuit_description: Descripción del circuito
            gates_sequence: Secuencia de compuertas
            test_input: Entrada de prueba
            expected_output: Salida esperada
            user_answer: Respuesta del usuario
            
        Returns:
            Explicación técnica específica
        """
        correct = "correcta" if user_answer == expected_output else "incorrecta"
        
        prompt = f"""
        Explica ESPECÍFICAMENTE cómo funciona este circuito lógico.
        
        CIRCUITO: {circuit_description}
        COMPUERTAS: {gates_sequence}
        ENTRADA: {test_input}
        SALIDA ESPERADA: {expected_output}
        RESPUESTA USUARIO: {user_answer} ({correct})
        
        RESPUESTA MÁXIMO 100 PALABRAS.
        
        Explica:
        1. Cómo se evalúa paso a paso
        2. Por qué la salida es {expected_output}
        3. Corrección específica si el usuario erró
        
        NO uses explicaciones genéricas. Sé específico sobre ESTE circuito.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 300
                }
            )
            
            return response.text[:400]  # Limitar respuesta
            
        except Exception as e:
            logger.error(f"Error explicando circuito: {str(e)}")
            return f"Este circuito {circuit_description.lower()} evalúa la entrada {test_input} produciendo {expected_output}."
    

    async def explain_complex_logic_circuit(
        self, 
        pattern_data: Dict[str, Any],
        user_answer: Union[int, Dict[str, Any]],
        expected_output: Union[int, Dict[str, Any]],
        evaluation_result: Dict[str, Any],
        complexity_type: str
    ) -> str:
        """
        Explica circuitos lógicos con complejidad variable según dificultad.
        
        Args:
            pattern_data: Datos del patrón del circuito
            user_answer: Respuesta del usuario
            expected_output: Salida esperada
            evaluation_result: Resultado de la evaluación
            complexity_type: Tipo de complejidad
            
        Returns:
            Explicación específica según la complejidad
        """
        correct = evaluation_result.get("correct", False)
        correct_text = "correcta" if correct else "incorrecta"
        
        if complexity_type == "single_output":
            return await self._explain_simple_circuit(
                pattern_data, user_answer, expected_output, correct_text
            )
        
        elif complexity_type == "multiple_cases":
            return await self._explain_multiple_cases_circuit(
                pattern_data, user_answer, expected_output, evaluation_result
            )
        
        elif complexity_type == "pattern_analysis":
            return await self._explain_pattern_analysis_circuit(
                pattern_data, user_answer, expected_output, evaluation_result
            )
        
        else:
            return f"Respuesta {correct_text}. Análisis del circuito no disponible."
    
    async def generate_simple_logic_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """
        Método de compatibilidad para generar circuito simple.
        Redirige al método complejo con configuración simple.
        """
        complexity_config = {
            "complexity_type": "single_output",
            "cases_count": 1,
            "question_template": "¿Cuál es la salida final del circuito?"
        }
        
        try:
            return await self.generate_complex_logic_circuit(
                difficulty=difficulty,
                gates_count=gates_count,
                inputs_count=inputs_count,
                complexity_config=complexity_config
            )
        except Exception as e:
            logger.error(f"Error en compatibilidad de circuito simple: {str(e)}")
            # Fallback directo
            return self._get_fallback_simple_circuit_new(difficulty, gates_count, inputs_count)

    async def _explain_simple_circuit(
        self,
        pattern_data: Dict[str, Any],
        user_answer: int,
        expected_output: int,
        correct_text: str
    ) -> str:
        """Explica circuito simple (easy)."""
        pattern = pattern_data.get("pattern", [])
        input_values = pattern_data.get("input_values", [])
        
        steps_description = []
        for i, (gate, values) in enumerate(zip(pattern, input_values)):
            inputs = values[:-1]
            output = values[-1]
            steps_description.append(f"{gate}({','.join(map(str, inputs))})={output}")
        
        steps_text = "; ".join(steps_description)
        
        prompt = f"""
        Explica BREVEMENTE este circuito simple.
        
        PASOS: {steps_text}
        RESPUESTA USUARIO: {user_answer} ({correct_text})
        RESPUESTA CORRECTA: {expected_output}
        
        RESPUESTA MÁXIMO 80 PALABRAS.
        
        Explica paso a paso y por qué la respuesta es {expected_output}.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 250
                }
            )
            return response.text[:300]
        except:
            return f"Circuito ejecuta: {steps_text}. Salida correcta: {expected_output}."
    
    async def _explain_multiple_cases_circuit(
        self,
        pattern_data: Dict[str, Any],
        user_answer: Dict[str, Any],
        expected_output: Dict[str, Any],
        evaluation_result: Dict[str, Any]
    ) -> str:
        """Explica circuito con múltiples casos (medium)."""
        pattern = pattern_data.get("pattern", [])
        test_cases = pattern_data.get("test_cases", [])
        partial_score = evaluation_result.get("partial_score", 0.0)
        case_results = evaluation_result.get("case_results", {})
        
        prompt = f"""
        Explica este circuito con múltiples casos de prueba.
        
        COMPUERTAS: {pattern}
        CASOS: {len(test_cases)}
        PUNTUACIÓN: {partial_score:.1%}
        RESULTADOS POR CASO: {case_results}
        
        RESPUESTA MÁXIMO 100 PALABRAS.
        
        Explica:
        1. Cómo funciona el circuito con diferentes entradas
        2. Por qué algunos casos son correctos/incorrectos
        3. Patrón general del circuito
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 300
                }
            )
            return response.text[:350]
        except:
            return f"Circuito {' → '.join(pattern)} evaluado en {len(test_cases)} casos. Puntuación: {partial_score:.1%}."
    
    async def _explain_pattern_analysis_circuit(
        self,
        pattern_data: Dict[str, Any],
        user_answer: Dict[str, Any],
        expected_output: Dict[str, Any],
        evaluation_result: Dict[str, Any]
    ) -> str:
        """Explica circuito con análisis de patrones (hard)."""
        pattern = pattern_data.get("pattern", [])
        partial_score = evaluation_result.get("partial_score", 0.0)
        component_results = evaluation_result.get("component_results", {})
        
        expected_pattern = expected_output.get("pattern", [])
        expected_cycle = expected_output.get("cycle_length", 0)
        expected_final = expected_output.get("final_state", 0)
        
        prompt = f"""
        Explica este circuito con análisis de patrones complejos.
        
        COMPUERTAS: {pattern}
        PATRÓN ESPERADO: {expected_pattern}
        CICLO ESPERADO: {expected_cycle}
        ESTADO FINAL: {expected_final}
        PUNTUACIÓN: {partial_score:.1%}
        ANÁLISIS: {component_results}
        
        RESPUESTA MÁXIMO 120 PALABRAS.
        
        Explica:
        1. Cómo el circuito genera el patrón
        2. Por qué el ciclo tiene esa longitud
        3. Qué determina el estado final
        4. Correcciones necesarias si hay errores
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 400
                }
            )
            return response.text[:400]
        except:
            return f"Circuito {' → '.join(pattern)} genera patrón {expected_pattern} con ciclo de {expected_cycle}. Puntuación: {partial_score:.1%}."


    def _get_fallback_hangman_word(
        self, 
        difficulty: str, 
        topic: str, 
        word_length_range: Tuple[int, int]
    ) -> Dict[str, str]:
        """Genera palabra de respaldo específica para ahorcado."""
        fallback_words = {
            "procesador": {
                "easy": ("MEMORIA", "Almacena datos temporalmente", "Componente esencial para guardar información"),
                "medium": ("PIPELINE", "Ejecuta instrucciones en paralelo", "Técnica que mejora rendimiento del procesador"),
                "hard": ("SUPERESCALAR", "Arquitectura avanzada de CPU", "Ejecuta múltiples instrucciones por ciclo")
            },
            "memoria": {
                "easy": ("CACHE", "Memoria rápida", "Acelera acceso a datos frecuentes"),
                "medium": ("VIRTUAL", "Sistema de direccionamiento", "Permite usar más memoria de la física disponible"),
                "hard": ("COHERENCIA", "Consistencia de datos", "Mantiene integridad en sistemas multiprocesador")
            },
            "entrada_salida": {
                "easy": ("PUERTOS", "Interfaces de comunicación", "Permiten conexión con periféricos"),
                "medium": ("INTERRUPCIONES", "Señales de eventos", "Mecanismo para manejo de eventos asíncronos"),
                "hard": ("CONTROLADORES", "Gestores de dispositivos", "Software que maneja hardware específico")
            },
            "ensamblador": {
                "easy": ("REGISTROS", "Almacenamiento rápido", "Memoria interna del procesador"),
                "medium": ("DIRECCIONAMIENTO", "Método de acceso", "Forma de referenciar ubicaciones de memoria"),
                "hard": ("OPTIMIZACION", "Mejora de rendimiento", "Técnicas para código más eficiente")
            }
        }
        
        topic_words = fallback_words.get(topic, fallback_words["procesador"])
        word_data = topic_words.get(difficulty, topic_words["medium"])
        
        return {
            "word": word_data[0],
            "clue": word_data[1],
            "argument": word_data[2]
        }
    

    def _get_fallback_simple_circuit_new(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Fallback para circuito simple - CORREGIDO."""
        return {
            "pattern": ["AND", "OR"],  # Usar "pattern" en lugar de "gates_sequence"
            "input_values": [
                [1, 1, 1],
                [1, 0, 1]
            ],
            "expected_output": 1,
            "complexity_type": "single_output",
            "description": "Circuito AND seguido de OR - Fallback"
        }
    
    def _get_fallback_multiple_cases_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        cases_count: int
    ) -> Dict[str, Any]:
        """Fallback para múltiples casos - CORREGIDO."""
        return {
            "pattern": ["AND", "XOR", "OR"],  # Usar "pattern"
            "test_cases": [
                {
                    "case_id": "case1",
                    "input_values": [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
                    "expected_output": 1
                },
                {
                    "case_id": "case2",
                    "input_values": [[0, 1, 0], [0, 1, 1], [1, 0, 1]],
                    "expected_output": 1
                },
                {
                    "case_id": "case3",
                    "input_values": [[1, 0, 0], [0, 1, 1], [1, 1, 1]],
                    "expected_output": 1
                }
            ],
            "expected_output": {"case1": 1, "case2": 1, "case3": 1},
            "complexity_type": "multiple_cases",
            "description": "Circuito evaluado con múltiples casos - Fallback"
        }
    
    def _get_fallback_pattern_analysis_circuit(
        self, 
        difficulty: str, 
        gates_count: int
    ) -> Dict[str, Any]:
        """Fallback para análisis de patrones - CORREGIDO."""
        return {
            "pattern": ["XOR", "AND", "OR", "NOT"],  # Usar "pattern"
            "sequence_inputs": [
                [1, 0], [0, 1], [1, 1], [0, 0]
            ],
            "pattern_analysis": {
                "sequence": [1, 0, 1, 0, 1, 0, 1, 0],
                "pattern_type": "alternating",
                "cycle_length": 2,
                "final_state": 0,
                "frequency": {"0": 4, "1": 4}
            },
            "expected_output": {
                "pattern": [1, 0, 1, 0, 1, 0, 1, 0],
                "final_state": 0,
                "cycle_length": 2
            },
            "complexity_type": "pattern_analysis",
            "description": "Circuito que genera patrón alternante - Fallback"
        }

    # TAMBIÉN ACTUALIZAR el fallback del método original
    def _get_fallback_simple_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Fallback para circuito simple - COMPATIBILIDAD."""
        
        if difficulty == "easy" and gates_count == 2:
            return {
                "pattern": ["AND", "OR"],  # Cambiar de "gates_sequence" a "pattern"
                "input_values": [
                    [1, 1, 1],    # AND(1,1) = 1
                    [1, 0, 1]     # OR(1,0) = 1
                ],
                "expected_output": 1,
                "complexity_type": "single_output",
                "description": "Detector básico con AND seguido de OR"
            }
        
        elif difficulty == "medium" and gates_count == 3:
            return {
                "pattern": ["AND", "XOR", "OR"],
                "input_values": [
                    [1, 1, 1],    # AND(1,1) = 1
                    [1, 0, 1],    # XOR(1,0) = 1  
                    [1, 1, 1]     # OR(1,1) = 1
                ],
                "expected_output": 1,
                "complexity_type": "single_output",
                "description": "Circuito combinacional con AND, XOR y OR"
            }
        
        elif difficulty == "hard" and gates_count == 4:
            return {
                "pattern": ["NAND", "NOR", "XOR", "AND"],
                "input_values": [
                    [1, 1, 0],    # NAND(1,1) = 0
                    [0, 1, 0],    # NOR(0,1) = 0
                    [0, 0, 0],    # XOR(0,0) = 0
                    [0, 1, 0]     # AND(0,1) = 0
                ],
                "expected_output": 0,
                "complexity_type": "single_output",
                "description": "Circuito complejo con compuertas negadas"
            }
        
        else:
            # Fallback genérico simple
            return {
                "pattern": ["AND"],
                "input_values": [
                    [1, 0, 0]     # AND(1,0) = 0
                ],
                "expected_output": 0,
                "complexity_type": "single_output",
                "description": "Compuerta AND básica"
            }


    def _get_fallback_logic_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int
    ) -> Dict[str, Any]:
        """Genera circuito de respaldo específico."""
        circuits = {
            "easy": {
                "circuit_description": "Detector de entrada alta",
                "gates_sequence": ["AND_G1"],
                "gate_connections": {
                    "G1": {"inputs": ["IN1", "IN2"], "output": "OUT"}
                },
                "test_input": [1, 1],
                "expected_output": 1,
                "technical_purpose": "Detecta cuando ambas entradas están activas"
            },
            "medium": {
                "circuit_description": "Selector de mayoría",
                "gates_sequence": ["AND_G1", "AND_G2", "AND_G3", "OR_G4"],
                "gate_connections": {
                    "G1": {"inputs": ["IN1", "IN2"], "output": "G1_OUT"},
                    "G2": {"inputs": ["IN1", "IN3"], "output": "G2_OUT"},
                    "G3": {"inputs": ["IN2", "IN3"], "output": "G3_OUT"},
                    "G4": {"inputs": ["G1_OUT", "G2_OUT", "G3_OUT"], "output": "OUT"}
                },
                "test_input": [1, 1, 0],
                "expected_output": 1,
                "technical_purpose": "Selecciona la salida basada en mayoría de entradas"
            },
            "hard": {
                "circuit_description": "Comparador de igualdad",
                "gates_sequence": ["XOR_G1", "XOR_G2", "NOR_G3"],
                "gate_connections": {
                    "G1": {"inputs": ["IN1", "IN3"], "output": "G1_OUT"},
                    "G2": {"inputs": ["IN2", "IN4"], "output": "G2_OUT"},
                    "G3": {"inputs": ["G1_OUT", "G2_OUT"], "output": "OUT"}
                },
                "test_input": [1, 0, 1, 0],
                "expected_output": 1,
                "technical_purpose": "Compara si dos pares de bits son iguales"
            }
        }
        
        return circuits.get(difficulty, circuits["easy"])
    

    def _validate_pattern_diversity(self, circuit_data: Dict[str, Any], complexity_type: str) -> bool:
        """
        Valida que el patrón generado tenga suficiente diversidad educativa.
        
        Args:
            circuit_data: Datos del circuito generado
            complexity_type: Tipo de complejidad esperada
            
        Returns:
            True si el patrón es suficientemente diverso
        """
        try:
            pattern = circuit_data.get("pattern", [])
            
            # Validación básica: al menos 2 compuertas diferentes
            if len(set(pattern)) < max(1, len(pattern) - 1):
                logger.warning(f"Patrón poco diverso: {pattern}")
                return False
            
            # Validación por complejidad
            if complexity_type == "single_output":
                return self._validate_simple_diversity(circuit_data)
            elif complexity_type == "multiple_cases":
                return self._validate_multiple_cases_diversity(circuit_data)
            elif complexity_type == "pattern_analysis":
                return self._validate_pattern_analysis_diversity(circuit_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando diversidad: {str(e)}")
            return False
    
    def _validate_simple_diversity(self, circuit_data: Dict[str, Any]) -> bool:
        """Valida diversidad para circuitos simples."""
        pattern = circuit_data.get("pattern", [])
        input_values = circuit_data.get("input_values", [])
        expected_output = circuit_data.get("expected_output", 0)
        
        # No debe ser solo AND/OR básico
        basic_only = all(gate in ["AND", "OR"] for gate in pattern)
        if basic_only and len(pattern) > 1:
            logger.warning("Patrón demasiado básico para educación")
            return False
        
        # Debe tener variedad en las entradas
        if len(input_values) >= 2:
            all_same_inputs = all(row[:-1] == input_values[0][:-1] for row in input_values)
            if all_same_inputs:
                logger.warning("Entradas idénticas, poco educativo")
                return False
        
        return True
    
    def _validate_multiple_cases_diversity(self, circuit_data: Dict[str, Any]) -> bool:
        """Valida diversidad para múltiples casos."""
        expected_output = circuit_data.get("expected_output", {})
        test_cases = circuit_data.get("test_cases", [])
        
        # Las salidas deben ser variadas
        if isinstance(expected_output, dict):
            unique_outputs = set(expected_output.values())
            if len(unique_outputs) < 2:
                logger.warning(f"Salidas poco diversas: {expected_output}")
                return False
        
        # Los casos deben tener entradas diferentes
        if len(test_cases) >= 2:
            first_case_inputs = test_cases[0].get("input_values", [])
            all_same = all(
                case.get("input_values", []) == first_case_inputs 
                for case in test_cases[1:]
            )
            if all_same:
                logger.warning("Casos con entradas idénticas")
                return False
        
        return True
    
    def _validate_pattern_analysis_diversity(self, circuit_data: Dict[str, Any]) -> bool:
        """Valida diversidad para análisis de patrones."""
        expected_output = circuit_data.get("expected_output", {})
        pattern_sequence = expected_output.get("pattern", [])
        
        # El patrón debe tener variedad
        if len(pattern_sequence) > 0:
            unique_values = set(pattern_sequence)
            if len(unique_values) < 2:
                logger.warning(f"Secuencia poco diversa: {pattern_sequence}")
                return False
            
            # No debe ser demasiado simple (ej: [1,1,1,1,1,1])
            if len(unique_values) == 1:
                return False
            
            # Debe tener al menos 6 elementos para análisis
            if len(pattern_sequence) < 6:
                logger.warning("Secuencia demasiado corta para análisis")
                return False
        
        return True
    
    async def _regenerate_if_needed(
        self, 
        circuit_data: Dict[str, Any], 
        complexity_type: str,
        difficulty: str,
        gates_count: int,
        inputs_count: int,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Regenera el circuito si no cumple con los estándares de diversidad.
        
        Args:
            circuit_data: Datos del circuito original
            complexity_type: Tipo de complejidad
            difficulty: Nivel de dificultad
            gates_count: Número de compuertas
            inputs_count: Número de entradas
            max_retries: Máximo número de reintentos
            
        Returns:
            Circuito mejorado o fallback diverso
        """
        if self._validate_pattern_diversity(circuit_data, complexity_type):
            return circuit_data
        
        logger.info(f"Regenerando circuito para mayor diversidad (intentos restantes: {max_retries})")
        
        if max_retries > 0:
            # Intentar regenerar con parámetros más creativos
            try:
                if complexity_type == "single_output":
                    new_circuit = await self._generate_simple_circuit(difficulty, gates_count, inputs_count)
                elif complexity_type == "multiple_cases":
                    new_circuit = await self._generate_multiple_cases_circuit(difficulty, gates_count, inputs_count, 3)
                elif complexity_type == "pattern_analysis":
                    new_circuit = await self._generate_pattern_analysis_circuit(difficulty, gates_count, inputs_count)
                else:
                    return circuit_data
                
                return await self._regenerate_if_needed(
                    new_circuit, complexity_type, difficulty, gates_count, inputs_count, max_retries - 1
                )
                
            except Exception as e:
                logger.error(f"Error en regeneración: {str(e)}")
        
        # Si fallan los reintentos, usar fallback diverso garantizado
        logger.info("Usando fallback diverso garantizado")
        if complexity_type == "single_output":
            return self._get_diverse_fallback_simple(difficulty, gates_count, inputs_count)
        elif complexity_type == "multiple_cases":
            return self._get_diverse_fallback_multiple_cases(difficulty, gates_count, 3)
        elif complexity_type == "pattern_analysis":
            return self._get_diverse_fallback_pattern_analysis(difficulty, gates_count)
        
        return circuit_data
    
    # AGREGAR al método generate_complex_logic_circuit una llamada a validación
    
    async def generate_complex_logic_circuit(
        self, 
        difficulty: str, 
        gates_count: int, 
        inputs_count: int,
        complexity_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera un circuito lógico con complejidad variable según dificultad - CON VALIDACIÓN DE DIVERSIDAD.
        """
        complexity_type = complexity_config.get("complexity_type", "single_output")
        cases_count = complexity_config.get("cases_count", 1)
        
        try:
            if complexity_type == "single_output":
                circuit_data = await self._generate_simple_circuit(difficulty, gates_count, inputs_count)
            elif complexity_type == "multiple_cases":
                circuit_data = await self._generate_multiple_cases_circuit(difficulty, gates_count, inputs_count, cases_count)
            elif complexity_type == "pattern_analysis":
                circuit_data = await self._generate_pattern_analysis_circuit(difficulty, gates_count, inputs_count)
            else:
                # Fallback a simple
                circuit_data = await self._generate_simple_circuit(difficulty, gates_count, inputs_count)
            
            # VALIDAR Y REGENERAR SI ES NECESARIO
            validated_circuit = await self._regenerate_if_needed(
                circuit_data, complexity_type, difficulty, gates_count, inputs_count
            )
            
            logger.info(f"Circuito generado: {validated_circuit.get('description', 'Sin descripción')}")
            logger.info(f"Patrón: {validated_circuit.get('pattern', [])}")
            
            return validated_circuit
            
        except Exception as e:
            logger.error(f"Error completo en generación de circuito: {str(e)}")
            # Fallback final garantizado
            return self._get_emergency_diverse_circuit(complexity_type, difficulty)
    
    def _get_emergency_diverse_circuit(self, complexity_type: str, difficulty: str) -> Dict[str, Any]:
        """Circuito de emergencia garantizado diverso."""
        emergency_circuits = {
            "single_output": {
                "pattern": ["NAND", "XOR"],
                "input_values": [[1, 0, 1], [1, 1, 0]],
                "expected_output": 0,
                "complexity_type": "single_output",
                "description": "Circuito de emergencia NAND-XOR"
            },
            "multiple_cases": {
                "pattern": ["XOR", "NAND", "OR"],
                "test_cases": [
                    {"case_id": "case1", "input_values": [[0, 1, 1], [1, 0, 0], [0, 1, 1]], "expected_output": 1},
                    {"case_id": "case2", "input_values": [[1, 0, 1], [1, 0, 0], [0, 0, 0]], "expected_output": 0},
                    {"case_id": "case3", "input_values": [[1, 1, 0], [0, 1, 1], [1, 0, 1]], "expected_output": 1}
                ],
                "expected_output": {"case1": 1, "case2": 0, "case3": 1},
                "complexity_type": "multiple_cases",
                "description": "Circuito de emergencia multi-caso"
            },
            "pattern_analysis": {
                "pattern": ["XOR", "NAND", "NOR", "NOT"],
                "sequence_inputs": [[1, 0], [0, 1], [1, 1], [0, 0], [1, 0], [0, 1]],
                "expected_output": {
                    "pattern": [1, 0, 0, 1, 1, 0],
                    "final_state": 0,
                    "cycle_length": 3
                },
                "complexity_type": "pattern_analysis",
                "description": "Circuito de emergencia con análisis de patrones"
            }
        }
        
        return emergency_circuits.get(complexity_type, emergency_circuits["single_output"])

    def _get_fallback_assembly_exercise(
        self, 
        difficulty: str, 
        architecture: str, 
        error_type: str
    ) -> Dict[str, str]:
        """Genera ejercicio de ensamblador de respaldo específico."""
        exercises = {
            "MIPS_basic": {
                "buggy_code": "li $t0, 10\nli $t1, 5\nadd $t2, $t0, $t1\nsw $t2, 0($sp)",
                "expected_behavior": "Sumar dos números y guardar resultado",
                "hint": "Revisa el uso del stack pointer",
                "error_explanation": "sw necesita que $sp esté inicializado correctamente"
            },
            "MIPS_intermediate": {
                "buggy_code": "li $t0, 8\nli $t1, 2\ndiv $t0, $t1\nmflo $t2\nsw $t2, array($t0)",
                "expected_behavior": "Dividir y guardar en array",
                "hint": "Revisa el direccionamiento del array",
                "error_explanation": "array($t0) usa índice incorrecto, debería ser un offset fijo"
            },
            "x86_advanced": {
                "buggy_code": "mov eax, 10\nmov ebx, 5\nadd eax, ebx\npush eax\npop ebx\nsub eax, ebx",
                "expected_behavior": "El resultado debe ser 0 en eax",
                "hint": "Analiza las operaciones de stack",
                "error_explanation": "Después del pop ebx, eax y ebx son iguales, sub eax, ebx da 0 pero falta mfhi para remainder"
            }
        }
        
        return exercises.get(architecture, exercises["MIPS_basic"])
# Instancia global del servicio
llm_service = LLMService()