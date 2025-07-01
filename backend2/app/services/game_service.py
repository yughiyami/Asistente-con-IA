"""
Servicio principal para manejo de juegos educativos.
Coordina la lógica de todos los tipos de juegos.
"""

import random
import uuid
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import logging
import json
from app.schemas.games import (
    GameType, DifficultyLevel,
    WordleLetterResult
)
from app.services.gemini_service import GeminiService
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class GameService:
    """Servicio principal para gestión de juegos"""
    
    def __init__(self, gemini_service: GeminiService, redis_service: RedisService):
        """
        Inicializa el servicio con dependencias.
        
        Args:
            gemini_service: Servicio de Gemini para generar contenido
            redis_service: Servicio de Redis para persistencia
        """
        self.gemini = gemini_service
        self.redis = redis_service
        
        # Inicializar generadores específicos de juegos
        self.logic_generator = LogicGameGenerator()
        self.assembly_generator = AssemblyGameGenerator(gemini_service)
    
    # Métodos para Ahorcado
    async def create_hangman_game(
        self, 
        topic: Optional[str], 
        difficulty: DifficultyLevel
    ) -> Dict:
        """Crea un nuevo juego de ahorcado"""
        game_id = str(uuid.uuid4())
        
        # Generar palabra con Gemini
        word_data = await self.gemini.generate_hangman_word(topic, difficulty.value)
        word = word_data["word"].upper()
        
        # Estado inicial del juego
        game_state = {
            "game_id": game_id,
            "word": word,
            "clue": word_data["clue"],
            "argument": word_data["argument"],
            "guessed_letters": [],
            "incorrect_guesses": 0,
            "max_attempts": 6,
            "created_at": datetime.utcnow().isoformat(),
            "game_over": False,
            "win": False
        }
        
        # Guardar en Redis
        await self.redis.save_game_state(game_id, GameType.HANGMAN.value, game_state)
        
        # Retornar respuesta sin revelar la palabra
        return {
            "game_id": game_id,
            "word_length": len(word),
            "clue": word_data["clue"],
            "argument": word_data["argument"],
            "max_attempts": 6,
            "hidden_word": " ".join(["_"] * len(word))
        }
    
    async def guess_hangman(self, game_id: str, guess: str) -> Dict:
        """Procesa un intento en el juego de ahorcado"""
        # Obtener estado del juego
        game_state = await self.redis.get_game_state(game_id, GameType.HANGMAN.value)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        if game_state["game_over"]:
            raise ValueError("El juego ya terminó")
        
        guess = guess.upper()
        word = game_state["word"]
        
        # Verificar si es intento de palabra completa
        if len(guess) > 1:
            correct = guess == word
            if not correct:
                game_state["incorrect_guesses"] += 1
        else:
            # Intento de letra
            if guess in game_state["guessed_letters"]:
                raise ValueError("Letra ya intentada")
            
            game_state["guessed_letters"].append(guess)
            correct = guess in word
            
            if not correct:
                game_state["incorrect_guesses"] += 1
        
        # Construir palabra actual
        current_word = ""
        for letter in word:
            if letter in game_state["guessed_letters"] or (len(guess) > 1 and correct):
                current_word += letter + " "
            else:
                current_word += "_ "
        current_word = current_word.strip()
        
        # Verificar fin del juego
        remaining_attempts = game_state["max_attempts"] - game_state["incorrect_guesses"]
        win = all(letter in game_state["guessed_letters"] or (len(guess) > 1 and correct) 
                 for letter in word)
        game_over = win or remaining_attempts <= 0
        
        game_state["game_over"] = game_over
        game_state["win"] = win
        
        # Actualizar estado en Redis
        await self.redis.update_game_state(game_id, GameType.HANGMAN.value, game_state)
        
        return {
            "correct": correct,
            "current_word": current_word,
            "remaining_attempts": remaining_attempts,
            "game_over": game_over,
            "win": win,
            "correct_word": word if game_over else None
        }
    
    # Métodos para Wordle
    async def create_wordle_game(
        self, 
        topic: Optional[str], 
        difficulty: DifficultyLevel
    ) -> Dict:
        """Crea un nuevo juego de Wordle"""
        game_id = str(uuid.uuid4())
        
        # Generar palabra con Gemini
        word_data = await self.gemini.generate_wordle_word(topic, difficulty.value)
        word = word_data["word"].upper()
        
        # Validar que sea de 5 letras
        if len(word) != 5:
            # Fallback a palabra predefinida si Gemini falla
            word = random.choice(["CACHE", "STACK", "QUEUE", "LOGIC", "BYTES"])
            word_data["topic_hint"] = "Concepto fundamental de arquitectura de computadoras"
        
        # Estado inicial del juego
        game_state = {
            "game_id": game_id,
            "word": word,
            "topic_hint": word_data["topic_hint"],
            "explanation": word_data.get("explanation", ""),
            "attempts": [],
            "max_attempts": 6,
            "created_at": datetime.utcnow().isoformat(),
            "game_over": False,
            "win": False
        }
        
        # Guardar en Redis
        await self.redis.save_game_state(game_id, GameType.WORDLE.value, game_state)
        
        return {
            "game_id": game_id,
            "word_length": 5,
            "max_attempts": 6,
            "topic_hint": word_data["topic_hint"]
        }
    
    async def guess_wordle(self, game_id: str, word: str) -> Dict:
        """Procesa un intento en el juego de Wordle"""
        # Obtener estado del juego
        game_state = await self.redis.get_game_state(game_id, GameType.WORDLE.value)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        if game_state["game_over"]:
            raise ValueError("El juego ya terminó")
        
        word = word.upper()
        target_word = game_state["word"]
        
        # Evaluar cada letra
        results = []
        target_letters = list(target_word)
        
        # Primera pasada: marcar letras correctas
        for i, letter in enumerate(word):
            if letter == target_word[i]:
                results.append(WordleLetterResult.CORRECT)
                target_letters[i] = None  # Marcar como usada
            else:
                results.append(None)
        
        # Segunda pasada: marcar letras presentes
        for i, letter in enumerate(word):
            if results[i] is None:
                if letter in target_letters:
                    results[i] = WordleLetterResult.PRESENT
                    # Remover primera ocurrencia
                    target_letters[target_letters.index(letter)] = None
                else:
                    results[i] = WordleLetterResult.ABSENT
        
        # Agregar intento al historial
        game_state["attempts"].append({
            "word": word,
            "results": [r.value for r in results]
        })
        
        # Verificar fin del juego
        attempt_number = len(game_state["attempts"])
        win = word == target_word
        remaining_attempts = game_state["max_attempts"] - attempt_number
        game_over = win or remaining_attempts <= 0
        
        game_state["game_over"] = game_over
        game_state["win"] = win
        
        # Actualizar estado en Redis
        await self.redis.update_game_state(game_id, GameType.WORDLE.value, game_state)
        
        return {
            "results": results,
            "attempt_number": attempt_number,
            "remaining_attempts": remaining_attempts,
            "game_over": game_over,
            "win": win,
            "correct_word": target_word if game_over else None,
            "explanation": game_state["explanation"] if game_over else None
        }
    
    # Métodos para Juego de Lógica
    async def create_logic_game(self, difficulty: DifficultyLevel) -> Dict:
        """Crea un nuevo juego de lógica"""
        game_id = str(uuid.uuid4())
    
        # Generar juego según dificultad
        game_data = self.logic_generator.generate_game(difficulty)
    
        # Estado del juego
        game_state = {
            "game_id": game_id,
            "difficulty": difficulty.value,
            "circuit": game_data["circuit"],
            "expected_truth_table": game_data["expected_truth_table"],
            "created_at": datetime.utcnow().isoformat(),
            "solved": False
        }
    
        # Guardar en Redis
        await self.redis.save_game_state(game_id, GameType.LOGIC.value, game_state)
        
        # Retornar sin la respuesta esperada
        return {
            "game_id": game_id,
            "circuit": game_data["circuit"],
            "num_inputs": game_data["num_inputs"],
            "question": game_data["question"]
        }
    
    async def answer_logic(self, game_id: str, truth_table: List[Dict]) -> Dict:
        """Procesa una respuesta al juego de lógica"""
        # Obtener estado del juego
        game_state = await self.redis.get_game_state(game_id, GameType.LOGIC.value)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        if game_state["solved"]:
            raise ValueError("El juego ya fue resuelto")
        
        truth_table_dict = [row.dict() for row in truth_table]
        # Evaluar respuesta
        correct, score, explanation = self.logic_generator.evaluate_answer(
            truth_table_dict,
            game_state["expected_truth_table"]
        )
        
        game_state["solved"] = True
        await self.redis.update_game_state(game_id, GameType.LOGIC.value, game_state)
        
        return {
            "correct": correct,
            "score": score * 100,  # Convertir a porcentaje
            "explanation": explanation,
            "expected_truth_table": game_state["expected_truth_table"] if not correct else None
        }

    # Métodos para Juego de Ensamblador
    async def create_assembly_game(self, difficulty: DifficultyLevel) -> Dict:
        """Crea un nuevo juego de ensamblador"""
        game_id = str(uuid.uuid4())
        
        # Generar juego según dificultad
        game_data = self.assembly_generator.generate_game(difficulty)
        
        # Estado del juego
        game_state = {
            "game_id": game_id,
            "difficulty": difficulty.value,
            "code": game_data["code"],
            "error_type": game_data["error_type"],
            "correct_explanation": game_data["correct_explanation"],
            "created_at": datetime.utcnow().isoformat(),
            "solved": False
        }
        
        # Guardar en Redis
        await self.redis.save_game_state(game_id, GameType.ASSEMBLY.value, game_state)
        
        return {
            "game_id": game_id,
            "code": game_data["code"],
            "architecture": "x86",
            "expected_behavior": game_data["expected_behavior"],
            "hint": game_data["hint"]
        }
    
    async def answer_assembly(self, game_id: str, explanation: str) -> Dict:
        """Procesa una respuesta al juego de ensamblador"""
        # Obtener estado del juego
        game_state = await self.redis.get_game_state(game_id, GameType.ASSEMBLY.value)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        if game_state["solved"]:
            raise ValueError("El juego ya fue resuelto")
        
        # Evaluar respuesta con IA
        score, feedback = self.assembly_generator.evaluate_explanation(
            explanation,
             game_state["correct_explanation"],
             game_state["code"]
        )
        
        correct = score >= 70  # 70% o más se considera correcto
        
        game_state["solved"] = True
        await self.redis.update_game_state(game_id, GameType.ASSEMBLY.value, game_state)
        
        return {
            "correct": correct,
            "correct_explanation": game_state["correct_explanation"],
            "score": score,
            "feedback": feedback
        }
    
    def _hide_expected_output(self, output: Union[int, List[int], Dict]) -> Union[str, List[str], Dict]:
        """Oculta la salida esperada con placeholders"""
        if isinstance(output, int):
            return "?"
        elif isinstance(output, list):
            return ["?" for _ in output]
        elif isinstance(output, dict):
            return {k: "?" if isinstance(v, int) else ["?" for _ in v] 
                   for k, v in output.items()}
        return "?"
    
    def _get_complexity_feedback(
        self, 
        complexity_type: str, 
        correct: bool, 
        partial_score: Optional[float]
    ) -> str:
        """Genera retroalimentación sobre la complejidad"""
        if correct:
            return "¡Excelente! Has demostrado comprensión completa de las compuertas lógicas."
        elif partial_score and partial_score > 0.5:
            return "Buen intento. Entiendes el concepto pero revisa los detalles de cada compuerta."
        else:
            return "Necesitas repasar las tablas de verdad de las compuertas básicas."


class LogicGameGenerator:
    """Generador de juegos de lógica"""
    
    def generate_game(self, difficulty: DifficultyLevel) -> Dict:
        """Genera un juego de lógica con circuito y tabla de verdad"""
        if difficulty == DifficultyLevel.EASY:
            # 2 entradas, 2-3 compuertas
            circuit = {
                "inputs": ["A", "B"],
                "gates": [
                    {"id": "G1", "type": "AND", "inputs": ["A", "B"]},
                    {"id": "G2", "type": "NOT", "inputs": ["G1"]},
                ],
                "output": "G2",
                "description": "A AND B, luego NOT"
            }
        elif difficulty == DifficultyLevel.MEDIUM:
            # 3 entradas, 3-4 compuertas
            circuit = {
                "inputs": ["A", "B", "C"],
                "gates": [
                    {"id": "G1", "type": "AND", "inputs": ["A", "B"]},
                    {"id": "G2", "type": "OR", "inputs": ["B", "C"]},
                    {"id": "G3", "type": "XOR", "inputs": ["G1", "G2"]},
                ],
                "output": "G3",
                "description": "(A AND B) XOR (B OR C)"
            }
        else:
            # 3 entradas, 4-5 compuertas complejas
            circuit = {
                "inputs": ["A", "B", "C"],
                "gates": [
                    {"id": "G1", "type": "AND", "inputs": ["A", "B"]},
                    {"id": "G2", "type": "NOT", "inputs": ["C"]},
                    {"id": "G3", "type": "OR", "inputs": ["G1", "G2"]},
                    {"id": "G4", "type": "AND", "inputs": ["B", "C"]},
                    {"id": "G5", "type": "XOR", "inputs": ["G3", "G4"]},
                ],
                "output": "G5",
                "description": "((A AND B) OR NOT(C)) XOR (B AND C)"
            }
        
        # Calcular tabla de verdad esperada
        truth_table = self._calculate_truth_table(circuit)
        
        return {
            "circuit": circuit,
            "expected_truth_table": truth_table,
            "num_inputs": len(circuit["inputs"]),
            "question": "Completa la tabla de verdad para este circuito"
        }
    
    def _calculate_truth_table(self, circuit: Dict) -> List[Dict]:
        """Calcula la tabla de verdad completa del circuito"""
        inputs = circuit["inputs"]
        num_inputs = len(inputs)
        truth_table = []
        
        # Generar todas las combinaciones posibles
        for i in range(2 ** num_inputs):
            # Crear valores de entrada
            input_values = {}
            for j, input_name in enumerate(inputs):
                input_values[input_name] = (i >> (num_inputs - 1 - j)) & 1
            
            # Calcular salida
            gate_outputs = {}
            for gate in circuit["gates"]:
                output = self._evaluate_gate(
                    gate["type"], 
                    gate["inputs"], 
                    input_values, 
                    gate_outputs
                )
                gate_outputs[gate["id"]] = output
            
            # Obtener salida final
            final_output = gate_outputs[circuit["output"]]
            
            # Agregar fila a la tabla
            row = {
                "inputs": input_values.copy(),
                "output": final_output
            }
            truth_table.append(row)
        
        return truth_table
    
    def _evaluate_gate(self, gate_type: str, inputs: List[str], 
                      input_values: Dict, gate_outputs: Dict) -> int:
        """Evalúa una compuerta lógica"""
        # Obtener valores de entrada
        values = []
        for inp in inputs:
            if inp in input_values:
                values.append(input_values[inp])
            else:
                values.append(gate_outputs[inp])
        
        # Evaluar según tipo
        if gate_type == "AND":
            return 1 if all(values) else 0
        elif gate_type == "OR":
            return 1 if any(values) else 0
        elif gate_type == "NOT":
            return 1 - values[0]
        elif gate_type == "XOR":
            return values[0] ^ values[1]
        elif gate_type == "NAND":
            return 1 - (1 if all(values) else 0)
        elif gate_type == "NOR":
            return 1 - (1 if any(values) else 0)
        elif gate_type == "XNOR":
            return 1 - (values[0] ^ values[1])
        
        return 0
    
    def evaluate_answer(self, user_table: List[Dict], expected_table: List[Dict]) -> Tuple[bool, float, str]:
        """Evalúa la tabla de verdad del usuario"""
        if len(user_table) != len(expected_table):
            return False, 0.0, "La tabla debe tener {} filas".format(len(expected_table))
        
        correct_rows = 0
        errors = []
        
        for i, (user_row, expected_row) in enumerate(zip(user_table, expected_table)):
            # Verificar que los inputs coincidan
            if user_row["inputs"] != expected_row["inputs"]:
                return False, 0.0, "Los valores de entrada no coinciden con los esperados"
            
            # Verificar output
            if user_row["output"] == expected_row["output"]:
                correct_rows += 1
            else:
                input_str = ", ".join(f"{k}={v}" for k, v in user_row["inputs"].items())
                errors.append(f"Fila {i+1} ({input_str}): esperado {expected_row['output']}, recibido {user_row['output']}")
        
        score = correct_rows / len(expected_table)
        
        if score == 1.0:
            return True, 1.0, "¡Perfecto! Tabla de verdad completamente correcta."
        else:
            error_msg = "Errores encontrados:\n" + "\n".join(errors[:3])  # Mostrar máx 3 errores
            if len(errors) > 3:
                error_msg += f"\n... y {len(errors) - 3} errores más"
            return False, score, error_msg

class AssemblyGameGenerator:
    """Generador de juegos de ensamblador Intel x86"""
    
    def __init__(self, gemini_service: GeminiService):
        self.gemini = gemini_service
    
    def generate_game(self, difficulty: DifficultyLevel) -> Dict:
        """Genera un juego de ensamblador con IA"""
        prompt = """Genera un ejercicio de código ensamblador Intel x86 con un error.
        
        Responde SOLO con un JSON válido con este formato exacto:
        {
            "code": "código ensamblador con error",
            "error_type": "tipo de error",
            "expected_behavior": "qué debería hacer el código",
            "hint": "pista para el estudiante",
            "correct_explanation": "explicación correcta del error"
        }
        
        El código debe ser simple, educativo y contener UN error claro.
        Tipos de error posibles: registro_no_inicializado, overflow, segmento_incorrecto, 
        division_mal_configurada, stack_desbalanceado, error_logico.
        """
        
        try:
            response = self.gemini.model.generate_content(prompt)

            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remover ```json
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remover ```
            cleaned_text = cleaned_text.strip()

            game_data = json.loads(cleaned_text)

            return game_data
        except Exception as e:
            logger.error(f"Error generando essamblador: {str(e)}")
            raise
    
    def evaluate_explanation(
        self, 
        user_explanation: str,
        correct_explanation: str,
        code: str
    ) -> Tuple[float, str]:
        """Evalúa la explicación usando IA"""
        prompt = f"""Evalúa la explicación del estudiante sobre un error en código ensamblador.

        Código con error:
        {code}
        
        Explicación correcta:
        {correct_explanation}
        
        Explicación del estudiante:
        {user_explanation}
        
        Responde SOLO con un JSON:
        {{
            "score": número entre 0 y 100,
            "feedback": "retroalimentación constructiva"
        }}
        
        Criterios de evaluación:
        - 80-100: Identifica correctamente el error y propone solución
        - 60-79: Identifica el error pero falta detalle
        - 40-59: Comprensión parcial
        - 0-39: No identifica el error correctamente
        """
        
        try:
            response = self.gemini.model.generate_content(prompt)
            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remover ```json
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remover ```
            cleaned_text = cleaned_text.strip()

            result = json.loads(cleaned_text)
            return result["score"], result["feedback"]
        except Exception:
            # Evaluación básica si falla IA
            if len(user_explanation) > 30:
                return 50.0, "Respuesta recibida. Intenta ser más específico sobre el error."
            return 20.0, "Respuesta muy corta. Explica detalladamente el error."