import os
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Tuple
import logging

from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite',system_instruction=settings.SYSTEM_PROMPT)
        self.chat_sessions = {}
    
    async def get_chat_response(self, message: str, session_id: str, mode: str = "chat") -> Dict[str, Any]:
        """Obtiene respuesta del modelo para un mensaje en modo chat"""
        try:
            # Crear nueva sesión si no existe
            if session_id not in self.chat_sessions:

                self.chat_sessions[session_id] = self.model.start_chat(enable_automatic_function_calling=True)
            
            # Ajustar prompt según modo
            if mode == "chat":
                prompt = f"Responde a esta pregunta sobre arquitectura de computadoras: {message}. Si es relevante, indica qué imágenes serían útiles incluir, marcándolas con IMAGEN_SUGERIDA: [descripción]."
            else:
                prompt = message
            
            # Obtener respuesta
            chat = self.chat_sessions[session_id]
            print(chat.history)
            response = await chat.send_message_async(prompt)
            
            text_response = response.text
            
            # Extraer sugerencias de imágenes
            images = []
            if "IMAGEN_SUGERIDA:" in text_response:
                # Extraer sugerencias de imágenes y eliminarlas del texto
                import re
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
    
    async def generate_exam(self, topic: str, difficulty: str = "medium", question_count: int = 10) -> Dict[str, Any]:
        """Genera un examen con preguntas de opción múltiple y respuesta abierta"""
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
            import re
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
    
    async def evaluate_exam(self, exam_data: Dict[str, Any], user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa las respuestas del examen y proporciona retroalimentación"""
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
                    import re
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
    
    async def initialize_game(self, game_type: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Inicializa un juego educativo del tipo especificado"""
        game_state = {}
        
        if game_type == "cache_simulator":
            # Simulador de Memoria Cache
            game_state = {
                "type": "cache_simulator",
                "cache_size": config.get("cache_size", 8),
                "blocks": [],
                "memory": [f"0x{i:04X}" for i in range(0, 256, 16)],
                "hits": 0,
                "misses": 0,
                "current_step": 0,
                "completed": False,
                "instructions": "Este simulador te ayuda a comprender cómo funciona la memoria caché. "
                               "Selecciona direcciones de memoria para ver si producen un hit o miss en caché."
            }
            
        elif game_type == "binary_converter":
            # Conversor Binario Interactivo
            game_state = {
                "type": "binary_converter",
                "current_challenge": None,
                "score": 0,
                "challenges_completed": 0,
                "max_challenges": 10,
                "completed": False,
                "instructions": "Convierte entre diferentes sistemas numéricos (binario, decimal, hexadecimal) "
                               "para mejorar tu comprensión de la representación de datos."
            }
            # Generar primer desafío
            game_state["current_challenge"] = self._generate_binary_challenge()
            
        elif game_type == "logic_circuits":
            # Constructor de Circuitos Lógicos
            game_state = {
                "type": "logic_circuits",
                "components": ["AND", "OR", "NOT", "XOR", "NAND", "NOR"],
                "current_challenge": None,
                "score": 0,
                "completed": False,
                "instructions": "Construye circuitos lógicos para implementar la función especificada "
                               "utilizando las compuertas disponibles."
            }
            # Generar desafío
            game_state["current_challenge"] = {
                "description": "Implementa un circuito que muestre '1' solo cuando exactamente una entrada es '1'",
                "inputs": 2,
                "expected_outputs": [[0,0,0], [0,1,1], [1,0,1], [1,1,0]],  # [A,B,Out]
                "hint": "Piensa en una función XOR"
            }
            
        elif game_type == "assembler":
            # Ensamblador Interactivo
            game_state = {
                "type": "assembler",
                "architecture": "MIPS",
                "registers": {"$zero": 0, "$at": 0, "$v0": 0, "$v1": 0, "$a0": 0, "$a1": 0, "$a2": 0, "$a3": 0,
                              "$t0": 0, "$t1": 0, "$t2": 0, "$t3": 0, "$t4": 0, "$t5": 0, "$t6": 0, "$t7": 0,
                              "$s0": 0, "$s1": 0, "$s2": 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0,
                              "$t8": 0, "$t9": 0, "$gp": 0, "$sp": 0, "$fp": 0, "$ra": 0},
                "memory": {},
                "pc": 0,
                "current_challenge": None,
                "score": 0,
                "completed": False,
                "instructions": "Escribe código en lenguaje ensamblador MIPS para resolver problemas simples. "
                               "Aprenderás sobre registros, instrucciones y el flujo de ejecución."
            }
            # Generar desafío
            game_state["current_challenge"] = {
                "description": "Escribe un programa en MIPS que sume los valores de $t0 y $t1 y guarde el resultado en $t2",
                "initial_state": {"$t0": 5, "$t1": 7},
                "expected_result": {"$t2": 12},
                "hint": "Usa la instrucción add"
            }
            
        elif game_type == "hangman":
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
            
        elif game_type == "word_scramble":
            # Juego de palabras desordenadas
            words = ["PROCESADOR", "PIPELINE", "COMPUTADORA", "ARQUITECTURA", "MEMORIA", "REGISTRO", "CACHÉ", "ENSAMBLADOR"]
            from random import choice, shuffle
            word = choice(words)
            scrambled = list(word)
            shuffle(scrambled)
            
            game_state = {
                "type": "word_scramble",
                "original_word": word,
                "scrambled_word": "".join(scrambled),
                "completed": False,
                "won": False,
                "attempts": 0,
                "max_attempts": 3,
                "hint": self._get_hangman_hint(word),
                "instructions": "Reordena las letras para formar una palabra relacionada con "
                               "arquitectura de computadoras."
            }
        
        return game_state
    
    async def process_game_action(self, game_state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa una acción en un juego y actualiza el estado"""
        game_type = game_state.get("type", "")
        action_type = action.get("action", "")
        action_data = action.get("data", {})
        
        # Copia del estado actual para modificar
        new_state = game_state.copy()
        message = None
        
        # Procesar acción según el tipo de juego
        if game_type == "cache_simulator":
            if action_type == "access_memory":
                address = action_data.get("address")
                if address:
                    hit, new_state = self._process_cache_access(new_state, address)
                    message = f"Acceso a {address}: {'Hit' if hit else 'Miss'}"
            
            elif action_type == "reset":
                new_state["blocks"] = []
                new_state["hits"] = 0
                new_state["misses"] = 0
                new_state["current_step"] = 0
                message = "Simulador reiniciado"
        
        elif game_type == "binary_converter":
            if action_type == "submit_answer":
                user_answer = action_data.get("answer")
                challenge = new_state.get("current_challenge", {})
                
                if challenge and user_answer:
                    correct = self._check_binary_answer(challenge, user_answer)
                    
                    if correct:
                        new_state["score"] += 1
                        message = "¡Correcto!"
                    else:
                        message = f"Incorrecto. La respuesta correcta era: {challenge.get('correct_answer')}"
                    
                    new_state["challenges_completed"] += 1
                    
                    # Generar nuevo desafío o finalizar
                    if new_state["challenges_completed"] >= new_state["max_challenges"]:
                        new_state["completed"] = True
                        new_state["current_challenge"] = None
                        message = f"¡Juego completado! Puntuación final: {new_state['score']}/{new_state['max_challenges']}"
                    else:
                        new_state["current_challenge"] = self._generate_binary_challenge()
        
        elif game_type == "hangman":
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
        
        elif game_type == "word_scramble":
            if action_type == "submit_word":
                guess = action_data.get("word", "").upper()
                
                if guess:
                    new_state["attempts"] += 1
                    
                    if guess == new_state["original_word"]:
                        new_state["completed"] = True
                        new_state["won"] = True
                        message = f"¡Correcto! Has descifrado la palabra: {new_state['original_word']}"
                    else:
                        if new_state["attempts"] >= new_state["max_attempts"]:
                            new_state["completed"] = True
                            message = f"Has agotado tus intentos. La palabra correcta era: {new_state['original_word']}"
                        else:
                            remaining = new_state["max_attempts"] - new_state["attempts"]
                            message = f"Incorrecto. Te quedan {remaining} {'intento' if remaining == 1 else 'intentos'}."
        
        # Para otros tipos de juegos se implementaría lógica similar
        
        return {
            "state": new_state,
            "message": message
        }
    
    def _generate_binary_challenge(self) -> Dict[str, Any]:
        """Genera un desafío para el conversor binario"""
        import random
        
        challenge_types = [
            "decimal_to_binary",
            "binary_to_decimal",
            "decimal_to_hex",
            "hex_to_decimal",
            "binary_to_hex",
            "hex_to_binary"
        ]
        
        challenge_type = random.choice(challenge_types)
        
        if challenge_type == "decimal_to_binary":
            decimal = random.randint(0, 255)
            return {
                "type": challenge_type,
                "question": f"Convierte el número decimal {decimal} a binario",
                "value": decimal,
                "correct_answer": bin(decimal)[2:].zfill(8)
            }
        elif challenge_type == "binary_to_decimal":
            decimal = random.randint(0, 255)
            binary = bin(decimal)[2:].zfill(8)
            return {
                "type": challenge_type,
                "question": f"Convierte el número binario {binary} a decimal",
                "value": binary,
                "correct_answer": str(decimal)
            }
        elif challenge_type == "decimal_to_hex":
            decimal = random.randint(0, 255)
            return {
                "type": challenge_type,
                "question": f"Convierte el número decimal {decimal} a hexadecimal",
                "value": decimal,
                "correct_answer": hex(decimal)[2:].upper()
            }
        elif challenge_type == "hex_to_decimal":
            decimal = random.randint(0, 255)
            hexa = hex(decimal)[2:].upper()
            return {
                "type": challenge_type,
                "question": f"Convierte el número hexadecimal {hexa} a decimal",
                "value": hexa,
                "correct_answer": str(decimal)
            }
        elif challenge_type == "binary_to_hex":
            decimal = random.randint(0, 255)
            binary = bin(decimal)[2:].zfill(8)
            hexa = hex(decimal)[2:].upper()
            return {
                "type": challenge_type,
                "question": f"Convierte el número binario {binary} a hexadecimal",
                "value": binary,
                "correct_answer": hexa
            }
        elif challenge_type == "hex_to_binary":
            decimal = random.randint(0, 255)
            binary = bin(decimal)[2:].zfill(8)
            hexa = hex(decimal)[2:].upper()
            return {
                "type": challenge_type,
                "question": f"Convierte el número hexadecimal {hexa} a binario",
                "value": hexa,
                "correct_answer": binary
            }
    
    def _check_binary_answer(self, challenge: Dict[str, Any], user_answer: str) -> bool:
        """Verifica si la respuesta del usuario es correcta para un desafío de conversión"""
        challenge_type = challenge.get("type", "")
        correct_answer = challenge.get("correct_answer", "")
        user_answer = user_answer.strip().upper()
        
        if challenge_type in ["decimal_to_binary", "binary_to_hex"]:
            # Remove leading zeros for binary output
            user_answer = user_answer.lstrip("0") or "0"
            correct_answer = correct_answer.lstrip("0") or "0"
        
        return user_answer == correct_answer
    
    def _process_cache_access(self, state: Dict[str, Any], address: str) -> Tuple[bool, Dict[str, Any]]:
        """Procesa un acceso a memoria en el simulador de caché"""
        cache_size = state.get("cache_size", 8)
        blocks = state.get("blocks", [])
        
        # Verificar si hay hit
        hit = address in blocks
        
        if hit:
            # Actualizar LRU moviendo el bloque al final (más recientemente usado)
            blocks.remove(address)
            blocks.append(address)
            state["hits"] += 1
        else:
            # Miss: agregar nuevo bloque
            if len(blocks) >= cache_size:
                # Caché llena, eliminar el bloque menos recientemente usado (LRU)
                blocks.pop(0)
            blocks.append(address)
            state["misses"] += 1
        
        state["blocks"] = blocks
        state["current_step"] += 1
        
        return hit, state
    
    def _get_hangman_hint(self, word: str) -> str:
        """Genera una pista para el juego del ahorcado"""
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

# Crear instancia global del servicio
ai_service = AIService()