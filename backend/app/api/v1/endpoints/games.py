"""
Endpoints para el modo Juegos.
Gestiona los diferentes juegos educativos: ahorcado, wordle, diagramas lógicos y ensamblador.
"""

import uuid
import logging
import json
from typing import Dict, List, Optional, Union
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


# Endpoint común para todos los juegos
@router.post("", response_model=Union[HangmanResponse, WordleResponse, LogicResponse, AssemblyResponse])
async def create_game(request: GameRequest):
    """
    Crea un nuevo juego del tipo especificado.
    
    Parameters:
    - **request**: Tipo de juego, dificultad y tema opcional
    
    Returns:
    - Objeto de juego específico según el tipo solicitado
    """
    # Redireccionar a la función específica según el tipo de juego
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


# Juego de Ahorcado (Hangman)
@router.post("/hangman", response_model=HangmanResponse)
async def create_hangman_game(request: GameRequest) -> HangmanResponse:
    """
    Crea un nuevo juego de Ahorcado.
    
    Parameters:
    - **request**: Configuración del juego
    
    Returns:
    - **HangmanResponse**: Juego de ahorcado configurado
    """
    try:
        # Generar prompt para el LLM
        prompt = f"""
        Genera una palabra relacionada con arquitectura de computadoras para un juego de ahorcado.
        Nivel de dificultad: {request.difficulty}
        Tema específico: {request.topic or "general"}
        
        Proporciona:
        1. Una palabra técnica relevante (sin espacios, solo letras)
        2. Una pista para ayudar a adivinar la palabra
        3. Una breve explicación sobre la palabra (para mostrar al final del juego)
        
        Formato JSON de respuesta:
        {{
          "word": "palabra",
          "clue": "Esta es una pista sobre la palabra",
          "argument": "Explicación detallada sobre el concepto"
        }}
        """
        
        # Configurar la estructura esperada para la respuesta JSON
        expected_structure = {
            "word": "ejemplo",
            "clue": "Esta es una pista",
            "argument": "Esta es una explicación"
        }
        
        # Llamar al LLM
        response_json = await llm_service.generate_json(prompt, expected_structure)
        
        # Extraer los valores
        word = response_json.get("word", "").upper()
        clue = response_json.get("clue", "")
        argument = response_json.get("argument", "")
        
        # Validar la palabra
        if not word or not word.isalpha():
            raise ValueError("La palabra generada no es válida")
        
        # Generar ID único para el juego
        game_id = f"hangman_{uuid.uuid4().hex}"
        
        # Guardar el juego en el servicio
        games_service.save_hangman_game(
            game_id=game_id,
            word=word,
            max_attempts=6
        )
        
        # Crear representación oculta de la palabra
        hidden_word = "_ " * len(word)
        
        return HangmanResponse(
            game_id=game_id,
            word_length=len(word),
            clue=clue,
            argument=argument,
            max_attempts=6,
            hidden_word=hidden_word.strip()
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de ahorcado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el juego de ahorcado"
        )


@router.post("/hangman/guess", response_model=HangmanGuessResponse)
async def guess_hangman(request: HangmanGuessRequest) -> HangmanGuessResponse:
    """
    Procesa un intento de adivinanza en el juego de Ahorcado.
    
    Parameters:
    - **request**: ID del juego y letra/palabra adivinada
    
    Returns:
    - **HangmanGuessResponse**: Resultado de la adivinanza
    """
    try:
        # Obtener el estado actual del juego
        game = games_service.get_hangman_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Verificar si el juego ya terminó
        if game.get("game_over", False):
            return HangmanGuessResponse(
                correct=False,
                current_word=game.get("current_word", ""),
                remaining_attempts=game.get("remaining_attempts", 0),
                game_over=True,
                win=game.get("win", False),
                correct_word=game.get("word", "")
            )
        
        # Procesar la adivinanza
        guess = request.guess.upper()
        word = game.get("word", "")
        current_word = game.get("current_word", "_ " * len(word)).split()
        remaining_attempts = game.get("remaining_attempts", 6)
        
        # Determinar si es adivinanza de letra o palabra completa
        if len(guess) == 1:  # Es una letra
            # Verificar si la letra está en la palabra
            correct = guess in word
            
            if correct:
                # Actualizar la palabra parcialmente revelada
                for i, char in enumerate(word):
                    if char == guess:
                        current_word[i] = char
            else:
                # Reducir intentos restantes
                remaining_attempts -= 1
                
        else:  # Es una palabra completa
            correct = guess == word
            
            if correct:
                # Revelar toda la palabra
                current_word = list(word)
            else:
                # Reducir intentos restantes
                remaining_attempts -= 1
        
        # Verificar si el juego ha terminado
        current_word_str = " ".join(current_word)
        game_over = remaining_attempts <= 0 or "_" not in current_word_str
        win = "_" not in current_word_str
        
        # Actualizar el estado del juego
        games_service.update_hangman_game(
            game_id=request.game_id,
            current_word=current_word_str,
            remaining_attempts=remaining_attempts,
            game_over=game_over,
            win=win
        )
        
        # Construir respuesta
        response = HangmanGuessResponse(
            correct=correct,
            current_word=current_word_str,
            remaining_attempts=remaining_attempts,
            game_over=game_over
        )
        
        # Incluir información adicional si el juego terminó
        if game_over:
            response.win = win
            response.correct_word = word
        
        return response
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error al procesar adivinanza: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la adivinanza"
        )


# Juego de Wordle
@router.post("/wordle", response_model=WordleResponse)
async def create_wordle_game(request: GameRequest) -> WordleResponse:
    """
    Crea un nuevo juego de Wordle con términos de arquitectura de computadoras.
    
    Parameters:
    - **request**: Configuración del juego
    
    Returns:
    - **WordleResponse**: Juego de Wordle configurado
    """
    try:
        # Generar prompt para el LLM
        prompt = f"""
        Genera una palabra de EXACTAMENTE 5 letras relacionada con arquitectura de computadoras para un juego de Wordle.
        Nivel de dificultad: {request.difficulty}
        Tema específico: {request.topic or "general"}
        
        La palabra debe ser un término técnico relevante y debe tener EXACTAMENTE 5 letras.
        Proporciona solo la palabra, sin espacios, solo letras.
        También incluye una pista sobre el tema de la palabra.
        
        Formato JSON de respuesta:
        {{
          "word": "palabra_de_5_letras",
          "topic_hint": "Pista sobre el tema de la palabra"
        }}
        """
        
        # Configurar la estructura esperada para la respuesta JSON
        expected_structure = {
            "word": "cache",
            "topic_hint": "Relacionado con almacenamiento de datos"
        }
        
        # Llamar al LLM
        response_json = await llm_service.generate_json(prompt, expected_structure)
        
        # Extraer los valores
        word = response_json.get("word", "").upper()
        topic_hint = response_json.get("topic_hint", "")
        
        # Validar la palabra (debe tener exactamente 5 letras)
        if not word or len(word) != 5 or not word.isalpha():
            # Si la palabra no es válida, usar una predeterminada
            fallback_words = ["CACHE", "STACK", "BUSES", "CLOCK", "RISC"]
            import random
            word = random.choice(fallback_words)
            logger.warning(f"Se generó una palabra no válida, usando alternativa: {word}")
        
        # Generar ID único para el juego
        game_id = f"wordle_{uuid.uuid4().hex}"
        
        # Guardar el juego en el servicio
        games_service.save_wordle_game(
            game_id=game_id,
            word=word,
            max_attempts=6
        )
        
        return WordleResponse(
            game_id=game_id,
            word_length=5,  # Siempre 5 para Wordle
            max_attempts=6,
            topic_hint=topic_hint
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de Wordle: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el juego de Wordle"
        )


@router.post("/wordle/guess", response_model=WordleGuessResponse)
async def guess_wordle(request: WordleGuessRequest) -> WordleGuessResponse:
    """
    Procesa un intento de adivinanza en el juego de Wordle.
    
    Parameters:
    - **request**: ID del juego y palabra adivinada
    
    Returns:
    - **WordleGuessResponse**: Resultado de la adivinanza con códigos de colores para cada letra
    """
    try:
        # Obtener el estado actual del juego
        game = games_service.get_wordle_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Verificar si el juego ya terminó
        if game.get("game_over", False):
            return WordleGuessResponse(
                results=[],
                attempt_number=game.get("attempts", [])[-1] if game.get("attempts") else 0,
                remaining_attempts=0,
                game_over=True,
                win=game.get("win", False),
                correct_word=game.get("word", ""),
                explanation=game.get("explanation", "")
            )
        
        # Procesar la adivinanza
        guess = request.word.upper()
        word = game.get("word", "")
        attempts = game.get("attempts", [])
        
        # Validar la palabra adivinada
        if len(guess) != 5 or not guess.isalpha():
            raise HTTPException(
                status_code=400, 
                detail="La palabra debe tener exactamente 5 letras y contener solo caracteres alfabéticos"
            )
        
        # Calcular resultados para cada letra
        results = []
        
        # Primero marcar las letras correctas en posición correcta
        word_chars = list(word)
        for i, char in enumerate(guess):
            if i < len(word) and char == word[i]:
                results.append(LetterResult.CORRECT)
                word_chars[i] = "*"  # Marcar como usada
            else:
                results.append(None)  # Temporal, se completará después
        
        # Luego marcar las letras presentes pero en posición incorrecta
        for i, char in enumerate(guess):
            if results[i] is None:  # Solo procesar posiciones aún sin resultado
                if char in word_chars:
                    results[i] = LetterResult.PRESENT
                    word_chars[word_chars.index(char)] = "*"  # Marcar como usada
                else:
                    results[i] = LetterResult.ABSENT
        
        # Actualizar el estado del juego
        attempts.append(guess)
        attempt_number = len(attempts)
        remaining_attempts = game.get("max_attempts", 6) - attempt_number
        
        # Verificar si el juego ha terminado
        win = guess == word
        game_over = win or remaining_attempts <= 0
        
        # Si el juego termina, generar una explicación del término
        explanation = None
        if game_over:
            try:
                # Generar explicación con el LLM
                explain_prompt = f"""
                Proporciona una explicación breve pero informativa sobre el término '{word.lower()}' 
                en el contexto de arquitectura de computadoras.
                La explicación debe ser clara y educativa, adecuada para un estudiante universitario.
                """
                explanation = await llm_service.generate_text(explain_prompt)
            except:
                explanation = f"Término técnico en arquitectura de computadoras: {word.lower()}"
        
        # Actualizar el estado del juego
        games_service.update_wordle_game(
            game_id=request.game_id,
            attempts=attempts,
            game_over=game_over,
            win=win,
            explanation=explanation
        )
        
        # Construir respuesta
        response = WordleGuessResponse(
            results=results,
            attempt_number=attempt_number,
            remaining_attempts=remaining_attempts,
            game_over=game_over
        )
        
        # Incluir información adicional si el juego terminó
        if game_over:
            response.win = win
            response.correct_word = word
            response.explanation = explanation
        
        return response
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error al procesar adivinanza de Wordle: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la adivinanza"
        )


# Juego de Diagrama Lógico
@router.post("/logic", response_model=LogicResponse)
async def create_logic_game(request: GameRequest) -> LogicResponse:
    """
    Crea un nuevo juego de Diagrama Lógico.
    
    Parameters:
    - **request**: Configuración del juego
    
    Returns:
    - **LogicResponse**: Juego de diagrama lógico configurado
    """
    try:
        # Generar prompt para el LLM
        prompt = f"""
        Crea un problema de diagrama lógico para arquitectura de computadoras.
        Nivel de dificultad: {request.difficulty}
        
        Proporciona:
        1. Un patrón o concepto lógico (por ejemplo, compuertas AND, OR, NOT, sumadores, multiplexores, etc.)
        2. Una pregunta desafiante sobre el patrón
        3. Valores de entrada de ejemplo (al menos 3 conjuntos de entradas)
        4. Valores de salida esperados para esas entradas
        
        Formato JSON de respuesta:
        {{
          "pattern": "descripción del patrón lógico",
          "question": "pregunta sobre el patrón",
          "input_values": [
            [valor1_conjunto1, valor2_conjunto1, ...],
            [valor1_conjunto2, valor2_conjunto2, ...],
            [valor1_conjunto3, valor2_conjunto3, ...]
          ],
          "expected_output": [
            resultado_conjunto1,
            resultado_conjunto2,
            resultado_conjunto3
          ]
        }}
        """
        
        # Configurar la estructura esperada para la respuesta JSON
        expected_structure = {
            "pattern": "Compuerta AND de 3 entradas",
            "question": "¿Cuál es la salida para cada conjunto de entradas?",
            "input_values": [[1, 1, 1], [1, 0, 1], [0, 1, 1]],
            "expected_output": [1, 0, 0]
        }
        
        # Llamar al LLM
        response_json = await llm_service.generate_json(prompt, expected_structure)
        
        # Extraer los valores
        pattern = response_json.get("pattern", "")
        question = response_json.get("question", "")
        input_values = response_json.get("input_values", [])
        expected_output = response_json.get("expected_output", [])
        
        # Validar valores
        if not pattern or not question or not input_values or not expected_output:
            raise ValueError("Los datos generados están incompletos")
        
        if len(input_values) != len(expected_output):
            raise ValueError("El número de entradas y salidas no coincide")
        
        # Generar ID único para el juego
        game_id = f"logic_{uuid.uuid4().hex}"
        
        # Guardar el juego en el servicio
        games_service.save_logic_game(
            game_id=game_id,
            pattern=pattern,
            question=question,
            input_values=input_values,
            expected_output=expected_output
        )
        
        return LogicResponse(
            game_id=game_id,
            pattern=pattern,
            question=question,
            input_values=input_values,
            expected_output=expected_output
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de diagrama lógico: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el juego de diagrama lógico"
        )


@router.post("/logic/answer", response_model=LogicAnswerResponse)
async def answer_logic(request: LogicAnswerRequest) -> LogicAnswerResponse:
    """
    Procesa la respuesta a un juego de Diagrama Lógico.
    
    Parameters:
    - **request**: ID del juego y respuestas proporcionadas
    
    Returns:
    - **LogicAnswerResponse**: Resultado de la validación con explicación
    """
    try:
        # Obtener el juego
        game = games_service.get_logic_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Comparar respuestas
        expected_output = game.get("expected_output", [])
        user_answers = request.answers
        
        # Verificar que el número de respuestas coincide
        if len(user_answers) != len(expected_output):
            raise HTTPException(
                status_code=400,
                detail=f"Número incorrecto de respuestas. Se esperaban {len(expected_output)}."
            )
        
        # Verificar respuestas
        all_correct = True
        for i, (user, expected) in enumerate(zip(user_answers, expected_output)):
            if str(user) != str(expected):  # Convertir a string para comparación flexible
                all_correct = False
                break
        
        # Generar explicación con el LLM
        explanation_prompt = f"""
        Explica el siguiente concepto de arquitectura de computadoras:
        
        Patrón: {game.get('pattern')}
        
        Proporciona una explicación detallada y educativa sobre cómo funciona este patrón lógico
        y por qué las entradas dadas producen las salidas esperadas.
        """
        
        explanation = await llm_service.generate_text(explanation_prompt)
        
        return LogicAnswerResponse(
            correct=all_correct,
            correct_answers=expected_output,
            explanation=explanation
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error al procesar respuesta de diagrama lógico: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la respuesta"
        )


# Juego de Ensamblador
@router.post("/assembly", response_model=AssemblyResponse)
async def create_assembly_game(request: GameRequest) -> AssemblyResponse:
    """
    Crea un nuevo juego de corrección de código ensamblador.
    
    Parameters:
    - **request**: Configuración del juego
    
    Returns:
    - **AssemblyResponse**: Juego de código ensamblador configurado
    """
    try:
        # Determinar la arquitectura según la dificultad
        architectures = {
            "easy": ["x86 básico", "MIPS básico"],
            "medium": ["x86", "MIPS", "ARM básico"],
            "hard": ["x86-64", "ARM", "RISC-V"]
        }
        
        import random
        difficulty = request.difficulty.lower()
        architecture = random.choice(architectures.get(difficulty, ["x86"]))
        
        # Generar prompt para el LLM
        prompt = f"""
        Crea un ejercicio de código ensamblador con errores para arquitectura de computadoras.
        Arquitectura: {architecture}
        Nivel de dificultad: {request.difficulty}
        
        Proporciona:
        1. Un fragmento de código en ensamblador con UN error o una parte faltante
        2. El comportamiento esperado del código cuando se corrija
        3. Una pista sobre dónde está el problema
        4. La solución correcta (para validación)
        
        El código debe ser simple pero educativo, relacionado con:
        {request.topic or "operaciones básicas, manejo de registros o memoria"}
        
        Formato JSON de respuesta:
        {{
          "code": "código ensamblador con el error",
          "expected_behavior": "comportamiento esperado cuando se corrige",
          "hint": "pista sobre el error",
          "solution": "código correcto o instrucción que soluciona el problema"
        }}
        """
        
        # Configurar la estructura esperada para la respuesta JSON
        expected_structure = {
            "code": "MOV AX, 5\nADD AX, 10\nMOV BX, AX\nSUB AX, BX\n; El resultado debería ser 0",
            "expected_behavior": "El programa debe calcular AX = 0",
            "hint": "Revisa cuidadosamente la instrucción SUB y sus operandos",
            "solution": "SUB AX, AX"
        }
        
        # Llamar al LLM
        response_json = await llm_service.generate_json(prompt, expected_structure)
        
        # Extraer los valores
        code = response_json.get("code", "")
        expected_behavior = response_json.get("expected_behavior", "")
        hint = response_json.get("hint", "")
        solution = response_json.get("solution", "")
        
        # Validar valores
        if not code or not expected_behavior or not hint or not solution:
            raise ValueError("Los datos generados están incompletos")
        
        # Generar ID único para el juego
        game_id = f"assembly_{uuid.uuid4().hex}"
        
        # Guardar el juego en el servicio
        games_service.save_assembly_game(
            game_id=game_id,
            code=code,
            architecture=architecture,
            expected_behavior=expected_behavior,
            hint=hint,
            solution=solution
        )
        
        return AssemblyResponse(
            game_id=game_id,
            code=code,
            architecture=architecture,
            expected_behavior=expected_behavior,
            hint=hint
        )
        
    except Exception as e:
        logger.error(f"Error al crear juego de ensamblador: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el juego de ensamblador"
        )


@router.post("/assembly/answer", response_model=AssemblyAnswerResponse)
async def answer_assembly(request: AssemblyAnswerRequest) -> AssemblyAnswerResponse:
    """
    Procesa la solución propuesta para un juego de código ensamblador.
    
    Parameters:
    - **request**: ID del juego y código corregido
    
    Returns:
    - **AssemblyAnswerResponse**: Resultado de la validación con explicación
    """
    try:
        # Obtener el juego
        game = games_service.get_assembly_game(request.game_id)
        
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Verificar la solución
        user_code = request.corrected_code
        solution = game.get("solution", "")
        
        # Verificar si la solución está presente en el código corregido
        is_correct = solution.strip() in user_code
        
        # Generar explicación
        if is_correct:
            explanation_prompt = f"""
            Explica por qué la siguiente corrección al código ensamblador es correcta:
            
            Problema: {game.get('expected_behavior')}
            Solución: {solution}
            
            Proporciona una explicación detallada y educativa, adecuada para un estudiante universitario.
            """
            
            explanation = await llm_service.generate_text(explanation_prompt)
        else:
            explanation = f"""
            Tu solución no es correcta. La clave para resolver este problema es:
            
            {game.get('hint')}
            
            Analiza cuidadosamente el código y el comportamiento esperado.
            """
        
        return AssemblyAnswerResponse(
            correct=is_correct,
            explanation=explanation,
            correct_solution=None if is_correct else solution
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error al procesar respuesta de ensamblador: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la respuesta"
        )