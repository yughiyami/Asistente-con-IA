"""
Endpoints para el modo Juegos.
Gestiona los diferentes juegos educativos: ahorcado, wordle, diagramas lógicos y ensamblador.
"""

import uuid
import logging
import json
from typing import Dict, List, Optional, Union , Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.schemas.games import (
    GameRequest, GameType, 
    HangmanResponse, HangmanGuessRequest, HangmanGuessResponse,
    WordleResponse, WordleGuessRequest, WordleGuessResponse, LetterResult,
    LogicResponse, LogicAnswerRequest, LogicAnswerResponse,
    AssemblyResponse, AssemblyAnswerRequest, AssemblyAnswerResponse
)
from app.services.llm import llm_service
from app.services.games import games_service

# Configurar logger
logger = logging.getLogger(__name__)

# Configurar router
router = APIRouter()

# Configuración de dificultad mejorada y específica
DIFFICULTY_CONFIG = {
    "easy": {
        "hangman": {"max_attempts": 8, "word_length_range": (6, 8), "hint_detail": "detailed"},
        "wordle": {"max_attempts": 7, "complexity": "basic_terms"},
        "logic": {"gates_count": 2, "inputs_count": 2, "complexity": "single_operation"},
        "assembly": {"instructions_count": 3, "architecture": "MIPS_basic", "error_type": "syntax"}
    },
    "medium": {
        "hangman": {"max_attempts": 6, "word_length_range": (8, 12), "hint_detail": "moderate"},
        "wordle": {"max_attempts": 6, "complexity": "intermediate_terms"},
        "logic": {"gates_count": 3, "inputs_count": 3, "complexity": "multi_gate"},
        "assembly": {"instructions_count": 5, "architecture": "MIPS_intermediate", "error_type": "logic"}
    },
    "hard": {
        "hangman": {"max_attempts": 5, "word_length_range": (12, 16), "hint_detail": "minimal"},
        "wordle": {"max_attempts": 5, "complexity": "advanced_terms"},
        "logic": {"gates_count": 4, "inputs_count": 4, "complexity": "complex_circuit"},
        "assembly": {"instructions_count": 7, "architecture": "x86_advanced", "error_type": "semantic"}
    }
}

# Tópicos específicos y mejorados por categoría
TOPICS_ENHANCED = {
    "procesador": {
        "easy": ["CPU básico", "ALU", "registros", "ciclo fetch"],
        "medium": ["pipeline", "superescalar", "branch prediction", "cache L1"],
        "hard": ["out-of-order execution", "speculative execution", "microarquitectura", "ROB"]
    },
    "memoria": {
        "easy": ["RAM", "ROM", "direcciones", "jerarquía"],
        "medium": ["cache coherencia", "memoria virtual", "TLB", "paginación"],
        "hard": ["NUMA", "cache protocols", "memory consistency", "cache partitioning"]
    },
    "entrada_salida": {
        "easy": ["puertos", "interrupciones", "DMA", "buses"],
        "medium": ["controladores", "polling vs interrupts", "bus arbitration", "I/O scheduling"],
        "hard": ["PCIe", "coherent interconnects", "IOMMU", "virtualized I/O"]
    },
    "ensamblador": {
        "easy": ["instrucciones básicas", "registros", "mov", "add"],
        "medium": ["saltos condicionales", "loops", "stack", "procedimientos"],
        "hard": ["optimización", "scheduling", "register allocation", "inline assembly"]
    }
}

COMPLEXITY_CONFIG = {
    "easy": {
        "complexity_type": "single_output",
        "description": "Una sola salida simple",
        "output_format": "int",  # Ejemplo: 1
        "evaluation_criteria": "exact_match",
        "question_template": "¿Cuál es la salida final del circuito?",
        "cases_count": 1
    },
    "medium": {
        "complexity_type": "multiple_cases", 
        "description": "Múltiples casos de prueba",
        "output_format": "dict",  # Ejemplo: {"case1": 0, "case2": 1, "case3": 1}
        "evaluation_criteria": "partial_scoring",
        "question_template": "¿Cuáles son las salidas para cada caso de prueba?",
        "cases_count": 3
    },
    "hard": {
        "complexity_type": "pattern_analysis",
        "description": "Análisis de patrones y múltiples circuitos",
        "output_format": "complex_dict",  # Ejemplo: {"pattern": [0,1,0,1], "final_state": 1, "cycle_length": 2}
        "evaluation_criteria": "pattern_recognition",
        "question_template": "Analiza el patrón de salidas y determina: el patrón completo, el estado final y la longitud del ciclo",
        "cases_count": 4
    }
}

# Tipos de análisis complejo para nivel hard
HARD_ANALYSIS_TYPES = [
    "pattern_sequence",     # Analizar secuencia de salidas
    "state_machine",        # Determinar estados de máquina
    "cycle_detection",      # Detectar ciclos en las salidas
    "frequency_analysis"    # Análisis de frecuencia de estados
]

# Endpoint común para todos los juegos (sin cambios)
@router.post("", response_model=Union[HangmanResponse, WordleResponse, LogicResponse, AssemblyResponse])
async def create_game(request: GameRequest):
    if request.game_type == GameType.HANGMAN:
        return await create_hangman_game(request)
    elif request.game_type == GameType.WORDLE:
        return await create_wordle_game(request)
    elif request.game_type == GameType.LOGIC:
        return await create_logic_game(request)
    elif request.game_type == GameType.ASSEMBLY:
        return await create_assembly_game(request)
    else:
        raise HTTPException(status_code=400, detail="Tipo de juego no soportado")

# Juego de Ahorcado - MEJORADO
@router.post("/hangman", response_model=HangmanResponse)
async def create_hangman_game(request: GameRequest) -> HangmanResponse:
    try:
        difficulty_config = DIFFICULTY_CONFIG[request.difficulty]["hangman"]
        topic_words = TOPICS_ENHANCED.get(request.topic, TOPICS_ENHANCED["procesador"])[request.difficulty]
        
        # Generar palabra específica con IA mejorada
        word_data = await llm_service.generate_hangman_word(
            difficulty=request.difficulty,
            topic=request.topic or "procesador",
            word_length_range=difficulty_config['word_length_range']
        )
        
        word = word_data["word"]
        clue = word_data["clue"]
        argument = word_data["argument"]
        
        game_id = f"hangman_{uuid.uuid4().hex}"
        
        games_service.save_hangman_game(
            game_id=game_id,
            word=word,
            clue=clue,
            argument=argument,
            max_attempts=difficulty_config["max_attempts"]
        )
        
        hidden_word = "_ " * len(word)
        
        return HangmanResponse(
            game_id=game_id,
            word_length=len(word),
            clue=clue[:100],  # Limitado a 100 caracteres
            argument=argument[:100],  # Limitado a 100 caracteres
            max_attempts=difficulty_config["max_attempts"],
            hidden_word=hidden_word.strip()
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de ahorcado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el juego de ahorcado")

@router.post("/hangman/guess", response_model=HangmanGuessResponse)
async def guess_hangman(request: HangmanGuessRequest) -> HangmanGuessResponse:
    try:
        game = games_service.get_hangman_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        if game.get("game_over", False):
            return HangmanGuessResponse(
                correct=False,
                current_word=game.get("current_word", ""),
                remaining_attempts=game.get("remaining_attempts", 0),
                game_over=True,
                win=game.get("win", False),
                correct_word=game.get("word", "")
            )
        
        # Procesar adivinanza usando el servicio
        updated_game = games_service.hangman_service.process_guess(request.game_id, request.guess)
        
        response = HangmanGuessResponse(
            correct=updated_game.get("last_guess_correct", False),
            current_word=updated_game.get("current_word", ""),
            remaining_attempts=updated_game.get("remaining_attempts", 0),
            game_over=updated_game.get("game_over", False)
        )
        
        if updated_game.get("game_over", False):
            response.win = updated_game.get("win", False)
            response.correct_word = updated_game.get("word", "")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar adivinanza: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la adivinanza")

# Juego de Wordle - SIN CAMBIOS MAYORES (mantener como está)
@router.post("/wordle", response_model=WordleResponse)
async def create_wordle_game(request: GameRequest) -> WordleResponse:
    try:
        # Generar palabra específica con IA
        prompt = f"""
        Genera UNA palabra de EXACTAMENTE 5 letras relacionada con arquitectura de computadoras.
        Dificultad: {request.difficulty}
        Tema: {request.topic or "general"}
        
        RESPUESTA LIMITADA A 100 PALABRAS MÁXIMO.
        
        Formato JSON:
        {{
          "word": "PALABRA_5_LETRAS",
          "topic_hint": "Pista específica (máximo 30 palabras)"
        }}
        """
        
        expected_structure = {"word": "CACHE", "topic_hint": "Relacionado con almacenamiento"}
        response_json = await llm_service.generate_json(prompt, expected_structure)
        
        word = response_json.get("word", "").upper()
        topic_hint = response_json.get("topic_hint", "")
        
        if not word or len(word) != 5 or not word.isalpha():
            fallback_words = ["CACHE", "STACK", "BUSES", "CLOCK", "RISC"]
            import random
            word = random.choice(fallback_words)
            logger.warning(f"Palabra no válida, usando alternativa: {word}")
        
        game_id = f"wordle_{uuid.uuid4().hex}"
        
        games_service.save_wordle_game(
            game_id=game_id,
            word=word,
            topic_hint=topic_hint,
            max_attempts=6
        )
        
        return WordleResponse(
            game_id=game_id,
            word_length=5,
            max_attempts=6,
            topic_hint=topic_hint[:100]  # Limitado a 100 caracteres
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de Wordle: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el juego de Wordle")

@router.post("/wordle/guess", response_model=WordleGuessResponse)
async def guess_wordle(request: WordleGuessRequest) -> WordleGuessResponse:
    try:
        game = games_service.get_wordle_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        if game.get("game_over", False):
            return WordleGuessResponse(
                results=[],
                attempt_number=len(game.get("attempts", [])),
                remaining_attempts=0,
                game_over=True,
                win=game.get("win", False),
                correct_word=game.get("word", ""),
                explanation=game.get("explanation", "")
            )
        
        # Procesar adivinanza usando el servicio
        updated_game = games_service.wordle_service.process_guess(request.game_id, request.word)
        
        # Obtener resultados de la última jugada
        results = updated_game.get("results", [])[-1] if updated_game.get("results") else []
        
        response = WordleGuessResponse(
            results=results,
            attempt_number=len(updated_game.get("attempts", [])),
            remaining_attempts=updated_game.get("max_attempts", 6) - len(updated_game.get("attempts", [])),
            game_over=updated_game.get("game_over", False)
        )
        
        if updated_game.get("game_over", False):
            response.win = updated_game.get("win", False)
            response.correct_word = updated_game.get("word", "")
            
            # Generar explicación limitada a 100 palabras
            if not updated_game.get("explanation"):
                explanation = await llm_service.generate_text(
                    f"Explica brevemente el término '{updated_game.get('word', '').lower()}' en arquitectura de computadoras (máximo 100 palabras)."
                )
                response.explanation = explanation[:400]  # Limitar a 400 caracteres total
            else:
                response.explanation = updated_game.get("explanation", "")[:400]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar adivinanza de Wordle: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la adivinanza")

# Juego de Diagrama Lógico - COMPLETAMENTE REDISEÑADO
@router.post("/logic", response_model=LogicResponse)
async def create_logic_game(request: GameRequest) -> LogicResponse:
    """
    Crea un nuevo juego de Compuertas Lógicas con complejidad variable según dificultad - CORREGIDO.
    """
    try:
        difficulty_config = DIFFICULTY_CONFIG[request.difficulty]["logic"]
        complexity_config = COMPLEXITY_CONFIG[request.difficulty]
        
        gates_count = difficulty_config["gates_count"]
        inputs_count = difficulty_config["inputs_count"]
        
        # Generar circuito con complejidad variable
        circuit_data = await llm_service.generate_complex_logic_circuit(
            difficulty=request.difficulty,
            gates_count=gates_count,
            inputs_count=inputs_count,
            complexity_config=complexity_config
        )
        
        game_id = f"logic_{uuid.uuid4().hex}"
        complexity_type = circuit_data.get("complexity_type", "single_output")
        
        # Preparar datos según tipo de complejidad
        if complexity_type == "single_output":
            pattern_list = circuit_data.get("pattern", [])
            input_matrix = circuit_data.get("input_values", [])
            expected_output = circuit_data.get("expected_output", 0)
            question = complexity_config.get("question_template", "¿Cuál es la salida final del circuito?")
            
        elif complexity_type == "multiple_cases":
            pattern_list = circuit_data.get("pattern", [])
            input_matrix = []  # Se usará test_cases en su lugar
            expected_output = circuit_data.get("expected_output", {})
            question = complexity_config.get("question_template", "¿Cuáles son las salidas para cada caso?")
            
            # Preparar matriz con todos los casos
            test_cases = circuit_data.get("test_cases", [])
            for case in test_cases:
                input_matrix.extend(case.get("input_values", []))
            
        elif complexity_type == "pattern_analysis":
            pattern_list = circuit_data.get("pattern", [])
            input_matrix = circuit_data.get("sequence_inputs", [])
            expected_output = circuit_data.get("expected_output", {})
            question = complexity_config.get("question_template", "Analiza el patrón y determina la secuencia.")
        
        else:
            # Fallback a simple
            pattern_list = circuit_data.get("pattern", ["AND"])
            input_matrix = circuit_data.get("input_values", [[1, 0, 0]])
            expected_output = circuit_data.get("expected_output", 0)
            question = "¿Cuál es la salida final del circuito?"
        
        # CORREGIR: Construir la estructura correcta con "pattern" en lugar de "gates_sequence"
        circuit_structure = {
            "pattern": pattern_list,  # USAR "pattern" aquí
            "input_values": input_matrix,
            "expected_output": expected_output,
            "complexity_type": complexity_type,
            "test_cases": circuit_data.get("test_cases", []),
            "difficulty": request.difficulty,
            "description": circuit_data.get("description", f"Circuito {complexity_type}")
        }
        
        # Guardar en el servicio con la estructura corregida
        games_service.save_logic_game(
            game_id=game_id,
            pattern=json.dumps(circuit_structure),  # Pasar estructura completa como JSON
            question=question,
            input_values=[input_matrix],  # Para compatibilidad
            expected_output=[expected_output] if isinstance(expected_output, (int, str)) else [expected_output]
        )
        
        return LogicResponse(
            game_id=game_id,
            difficulty=request.difficulty,
            pattern=pattern_list,
            question=question,
            input_values=input_matrix,
            expected_output=expected_output,
            complexity_type=complexity_type
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de lógica complejo: {str(e)}")
        # En caso de error, intentar con fallback simple
        try:
            return await _create_fallback_logic_game(request)
        except Exception as fallback_error:
            logger.error(f"Error en fallback de lógica: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail="Error al crear el juego de lógica")


# AGREGAR función de fallback
async def _create_fallback_logic_game(request: GameRequest) -> LogicResponse:
    """Crea un juego de lógica de fallback en caso de error."""
    game_id = f"logic_{uuid.uuid4().hex}"
    
    # Fallback simple según dificultad
    if request.difficulty == "easy":
        pattern_list = ["AND"]
        input_matrix = [[1, 1, 1]]
        expected_output = 1
        complexity_type = "single_output"
    elif request.difficulty == "medium":
        pattern_list = ["AND", "OR"]
        input_matrix = [[1, 1, 1], [1, 0, 1]]
        expected_output = {"case1": 1, "case2": 1}
        complexity_type = "multiple_cases"
    else:  # hard
        pattern_list = ["XOR", "NOT"]
        input_matrix = [[1, 0], [0, 1]]
        expected_output = {"pattern": [1, 0], "final_state": 0, "cycle_length": 2}
        complexity_type = "pattern_analysis"
    
    # Estructura de fallback
    circuit_structure = {
        "pattern": pattern_list,
        "input_values": input_matrix,
        "expected_output": expected_output,
        "complexity_type": complexity_type,
        "difficulty": request.difficulty,
        "description": f"Circuito fallback {complexity_type}"
    }
    
    question = COMPLEXITY_CONFIG[request.difficulty].get("question_template", "¿Cuál es la salida del circuito?")
    
    # Guardar en el servicio
    games_service.save_logic_game(
        game_id=game_id,
        pattern=json.dumps(circuit_structure),
        question=question,
        input_values=[input_matrix],
        expected_output=[expected_output] if isinstance(expected_output, (int, str)) else [expected_output]
    )
    
    logger.info(f"Juego de lógica fallback creado: {game_id}")
    
    return LogicResponse(
        game_id=game_id,
        difficulty=request.difficulty,
        pattern=pattern_list,
        question=question,
        input_values=input_matrix,
        expected_output=expected_output,
        complexity_type=complexity_type
    )

@router.post("/logic/answer", response_model=LogicAnswerResponse)
async def answer_logic(request: LogicAnswerRequest) -> LogicAnswerResponse:
    """
    Procesa la respuesta a un juego de Compuertas Lógicas con complejidad variable.
    """
    try:
        game = games_service.get_logic_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Obtener datos del juego
        pattern_data = json.loads(game.get('pattern', '{}'))
        complexity_type = pattern_data.get("complexity_type", "single_output")
        difficulty = pattern_data.get("difficulty", "easy")
        expected_output = pattern_data.get("expected_output", 0)
        user_answer = request.answer
        
        # Evaluar según complejidad
        if complexity_type == "single_output":
            evaluation_result = await _evaluate_simple_answer(
                user_answer, expected_output, pattern_data
            )
        elif complexity_type == "multiple_cases":
            evaluation_result = await _evaluate_multiple_cases_answer(
                user_answer, expected_output, pattern_data
            )
        elif complexity_type == "pattern_analysis":
            evaluation_result = await _evaluate_pattern_analysis_answer(
                user_answer, expected_output, pattern_data
            )
        else:
            # Fallback a evaluación simple
            evaluation_result = await _evaluate_simple_answer( # type: ignore
                user_answer, expected_output, pattern_data
            )
        
        # Generar explicación específica según complejidad
        explanation = await llm_service.explain_complex_logic_circuit(
            pattern_data=pattern_data,
            user_answer=user_answer,
            expected_output=expected_output,
            evaluation_result=evaluation_result,
            complexity_type=complexity_type
        )
        
        response = LogicAnswerResponse(
            correct=evaluation_result.get("correct", False),
            correct_answer=expected_output,
            explanation=explanation[:400]
        )
        
        # Agregar información adicional para respuestas complejas
        if complexity_type in ["multiple_cases", "pattern_analysis"]:
            response.partial_score = evaluation_result.get("partial_score")
            response.complexity_feedback = evaluation_result.get("feedback", "")[:200]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar respuesta de lógica compleja: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la respuesta")


async def _evaluate_simple_answer(
    user_answer: int,
    expected_output: int,
    pattern_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Evalúa respuesta simple (easy)."""
    correct = int(user_answer) == int(expected_output)
    return {
        "correct": correct,
        "score": 1.0 if correct else 0.0,
        "feedback": "Correcto" if correct else f"Incorrecto, la respuesta era {expected_output}"
    }


async def _evaluate_multiple_cases_answer(
    user_answer: Dict[str, int],
    expected_output: Dict[str, int],
    pattern_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Evalúa respuesta de múltiples casos (medium)."""
    if not isinstance(user_answer, dict) or not isinstance(expected_output, dict):
        return {"correct": False, "partial_score": 0.0, "feedback": "Formato de respuesta incorrecto"}
    
    total_cases = len(expected_output)
    correct_cases = 0
    
    case_results = {}
    for case_id, expected_val in expected_output.items():
        user_val = user_answer.get(case_id)
        if user_val is not None and int(user_val) == int(expected_val):
            correct_cases += 1
            case_results[case_id] = "correct"
        else:
            case_results[case_id] = f"incorrect (expected {expected_val}, got {user_val})"
    
    partial_score = correct_cases / total_cases
    all_correct = correct_cases == total_cases
    
    feedback = f"Casos correctos: {correct_cases}/{total_cases}"
    
    return {
        "correct": all_correct,
        "partial_score": partial_score,
        "case_results": case_results,
        "feedback": feedback
    }


async def _evaluate_pattern_analysis_answer(
    user_answer: Dict[str, Any],
    expected_output: Dict[str, Any],
    pattern_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Evalúa respuesta de análisis de patrones (hard)."""
    if not isinstance(user_answer, dict) or not isinstance(expected_output, dict):
        return {"correct": False, "partial_score": 0.0, "feedback": "Formato de respuesta incorrecto"}
    
    total_components = len(expected_output)
    correct_components = 0
    component_results = {}
    
    for component, expected_val in expected_output.items():
        user_val = user_answer.get(component)
        
        if component == "pattern":
            # Comparar listas de patrones
            if isinstance(user_val, list) and isinstance(expected_val, list):
                matches = sum(1 for u, e in zip(user_val, expected_val) if u == e)
                pattern_accuracy = matches / len(expected_val) if expected_val else 0
                if pattern_accuracy >= 0.8:  # 80% de precisión mínima
                    correct_components += 1
                    component_results[component] = f"correct ({pattern_accuracy:.1%} accuracy)"
                else:
                    component_results[component] = f"partial ({pattern_accuracy:.1%} accuracy)"
            else:
                component_results[component] = "incorrect format"
        else:
            # Comparar valores individuales
            if user_val == expected_val:
                correct_components += 1
                component_results[component] = "correct"
            else:
                component_results[component] = f"incorrect (expected {expected_val}, got {user_val})"
    
    partial_score = correct_components / total_components
    all_correct = correct_components == total_components
    
    feedback = f"Componentes correctos: {correct_components}/{total_components}"
    
    return {
        "correct": all_correct,
        "partial_score": partial_score,
        "component_results": component_results,
        "feedback": feedback
    }

# Juego de Ensamblador - COMPLETAMENTE REDISEÑADO
@router.post("/assembly", response_model=AssemblyResponse)
async def create_assembly_game(request: GameRequest) -> AssemblyResponse:
    try:
        difficulty_config = DIFFICULTY_CONFIG[request.difficulty]["assembly"]
        
        # Generar ejercicio específico con IA mejorada
        exercise_data = await llm_service.generate_assembly_exercise(
            difficulty=request.difficulty,
            architecture=difficulty_config["architecture"],
            error_type=difficulty_config["error_type"],
            instructions_count=difficulty_config["instructions_count"]
        )
        
        game_id = f"assembly_{uuid.uuid4().hex}"
        
        games_service.save_assembly_game(
            game_id=game_id,
            code=exercise_data.get("buggy_code", ""),
            architecture=difficulty_config["architecture"],
            expected_behavior=exercise_data.get("expected_behavior", ""),
            hint=exercise_data.get("hint", ""),
            solution=exercise_data.get("error_explanation", "")
        )
        
        return AssemblyResponse(
            game_id=game_id,
            code=exercise_data.get("buggy_code", ""),
            architecture=difficulty_config["architecture"],
            expected_behavior=exercise_data.get("expected_behavior", "")[:100],  # Limitado a 100 caracteres
            hint=exercise_data.get("hint", "")[:100]  # Limitado a 100 caracteres
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de ensamblador: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el juego de ensamblador")

@router.post("/assembly/answer", response_model=AssemblyAnswerResponse)
async def answer_assembly(request: AssemblyAnswerRequest) -> AssemblyAnswerResponse:
    try:
        game = games_service.get_assembly_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Evaluar explicación usando el servicio
        updated_game = games_service.assembly_service.evaluate_explanation(
            request.game_id,
            request.explanation  # Ahora solo se envía explicación
        )
        
        evaluation = updated_game.get("evaluation_result", {})
        is_correct = evaluation.get("correctness") in ["excellent", "good"]
        
        # Generar explicación específica limitada a 100 palabras
        if is_correct:
            explanation = evaluation.get("feedback", "¡Excelente análisis! Tu explicación demuestra comprensión del error.")
        else:
            explanation = evaluation.get("feedback", "Necesitas revisar tu análisis. ") + f" Error real: {game.get('solution', '')[:50]}"
        
        return AssemblyAnswerResponse(
            correct=is_correct,
            explanation=explanation[:400],  # Limitado a 400 caracteres
            correct_solution=None if is_correct else game.get('solution', '')[:100]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar respuesta de ensamblador: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la respuesta de ensamblador")