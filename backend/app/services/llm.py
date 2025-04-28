"""
Servicio de integración con el modelo de lenguaje Google Gemini.
Gestiona las solicitudes al modelo LLM y procesa las respuestas.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

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


# Instancia global del servicio
llm_service = LLMService()