"""
Servicio principal para la gestión de juegos educativos.
Proporciona una interfaz unificada para interactuar con los diferentes tipos de juegos.
"""

import logging
from typing import Dict, List, Optional, Any, Union

# Importar servicios específicos
from app.services.games.hangman import hangman_service
from app.services.games.wordle import wordle_service
from app.services.games.logic_diagram import logic_diagram_service
from app.services.games.assembly import assembly_service

# Configurar logger
logger = logging.getLogger(__name__)


class GamesService:
    """
    Servicio principal para gestionar todos los tipos de juegos educativos.
    
    Proporciona una interfaz unificada para:
    - Crear juegos de diferentes tipos
    - Recuperar estados de juegos
    - Actualizar juegos
    - Limpiar juegos antiguos
    """
    
    def __init__(self):
        """Inicializa el servicio principal de juegos."""
        # Referencia a los servicios específicos
        self.hangman_service = hangman_service
        self.wordle_service = wordle_service
        self.logic_diagram_service = logic_diagram_service
        self.assembly_service = assembly_service
    
    # Métodos para el juego de Ahorcado (Hangman)
    
    def save_hangman_game(
        self, 
        game_id: str, 
        word: str, 
        clue: str = "", 
        argument: str = "",
        max_attempts: int = 6
    ) -> Dict[str, Any]:
        """
        Crea un nuevo juego de Ahorcado.
        
        Args:
            game_id: Identificador único del juego
            word: Palabra a adivinar
            clue: Pista sobre la palabra
            argument: Explicación educativa sobre el término
            max_attempts: Número máximo de intentos permitidos
            
        Returns:
            Datos del juego creado
        """
        return self.hangman_service.create_game(
            game_id=game_id,
            word=word,
            clue=clue,
            argument=argument,
            max_attempts=max_attempts
        )
    
    def get_hangman_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un juego de Ahorcado por su ID.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Datos del juego o None si no existe
        """
        return self.hangman_service.get_game(game_id)
    
    def update_hangman_game(
        self, 
        game_id: str, 
        current_word: str,
        remaining_attempts: int,
        game_over: bool,
        win: bool
    ) -> bool:
        """
        Actualiza el estado de un juego de Ahorcado.
        
        Args:
            game_id: Identificador del juego
            current_word: Estado actual de la palabra
            remaining_attempts: Intentos restantes
            game_over: Si el juego ha terminado
            win: Si el jugador ha ganado
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        game = self.hangman_service.get_game(game_id)
        
        if not game:
            return False
        
        game.update({
            "current_word": current_word,
            "remaining_attempts": remaining_attempts,
            "game_over": game_over,
            "win": win
        })
        
        return True
    
    # Métodos para el juego de Wordle
    
    def save_wordle_game(
        self, 
        game_id: str, 
        word: str, 
        topic_hint: str = "",
        max_attempts: int = 6
    ) -> Dict[str, Any]:
        """
        Crea un nuevo juego de Wordle.
        
        Args:
            game_id: Identificador único del juego
            word: Palabra a adivinar (debe tener exactamente 5 letras)
            topic_hint: Pista sobre el tema de la palabra
            max_attempts: Número máximo de intentos permitidos
            
        Returns:
            Datos del juego creado
        """
        return self.wordle_service.create_game(
            game_id=game_id,
            word=word,
            topic_hint=topic_hint,
            max_attempts=max_attempts
        )
    
    def get_wordle_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un juego de Wordle por su ID.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Datos del juego o None si no existe
        """
        return self.wordle_service.get_game(game_id)
    
    def update_wordle_game(
        self, 
        game_id: str, 
        attempts: List[str],
        game_over: bool,
        win: bool,
        explanation: Optional[str] = None
    ) -> bool:
        """
        Actualiza el estado de un juego de Wordle.
        
        Args:
            game_id: Identificador del juego
            attempts: Lista de palabras intentadas
            game_over: Si el juego ha terminado
            win: Si el jugador ha ganado
            explanation: Explicación educativa (solo si el juego terminó)
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        game = self.wordle_service.get_game(game_id)
        
        if not game:
            return False
        
        game.update({
            "attempts": attempts,
            "game_over": game_over,
            "win": win
        })
        
        if game_over and explanation:
            game["explanation"] = explanation
        
        return True
    
    # Métodos para el juego de Diagrama Lógico
    
    def save_logic_game(
        self, 
        game_id: str, 
        pattern: str, 
        question: str,
        input_values: List[List[Union[int, str]]],
        expected_output: List[Union[int, str]]
    ) -> Dict[str, Any]:
        """
        Crea un nuevo juego de Diagrama Lógico.
        
        Args:
            game_id: Identificador único del juego
            pattern: Descripción del patrón lógico
            question: Pregunta sobre el patrón
            input_values: Lista de valores de entrada de ejemplo
            expected_output: Lista de valores de salida esperados
            
        Returns:
            Datos del juego creado
        """
        return self.logic_diagram_service.create_game(
            game_id=game_id,
            pattern=pattern,
            question=question,
            input_values=input_values,
            expected_output=expected_output
        )
    
    def get_logic_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un juego de Diagrama Lógico por su ID.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Datos del juego o None si no existe
        """
        return self.logic_diagram_service.get_game(game_id)
    

    
    # Métodos para el juego de Ensamblador
    
    def save_assembly_game(
        self, 
        game_id: str, 
        code: str, 
        architecture: str,
        expected_behavior: str,
        hint: str,
        solution: str
    ) -> Dict[str, Any]:
        """
        Crea un nuevo juego de Ensamblador.
        
        Args:
            game_id: Identificador único del juego
            code: Código en ensamblador con errores
            architecture: Arquitectura del ensamblador (MIPS, x86, etc.)
            expected_behavior: Comportamiento esperado del código
            hint: Pista sobre el error
            solution: Solución correcta para validación
            
        Returns:
            Datos del juego creado
        """
        return self.assembly_service.create_game(
            game_id=game_id,
            code=code,
            architecture=architecture,
            expected_behavior=expected_behavior,
            hint=hint,
            solution=solution
        )
    
    def get_assembly_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un juego de Ensamblador por su ID.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Datos del juego o None si no existe
        """
        return self.assembly_service.get_game(game_id)
    

    
    # Métodos generales para todos los juegos
    
    def clean_old_games(self, max_age_hours: int = 24) -> Dict[str, int]:
        """
        Limpia juegos antiguos de todos los tipos para liberar memoria.
        
        Args:
            max_age_hours: Edad máxima en horas para conservar juegos
            
        Returns:
            Diccionario con el número de juegos eliminados por tipo
        """
        hangman_deleted = self.hangman_service.clean_old_games(max_age_hours)
        wordle_deleted = self.wordle_service.clean_old_games(max_age_hours)
        logic_deleted = self.logic_diagram_service.clean_old_games(max_age_hours)
        assembly_deleted = self.assembly_service.clean_old_games(max_age_hours)
        
        total_deleted = hangman_deleted + wordle_deleted + logic_deleted + assembly_deleted
        
        logger.info(f"Limpieza general de juegos: {total_deleted} juegos eliminados")
        
        return {
            "hangman": hangman_deleted,
            "wordle": wordle_deleted,
            "logic": logic_deleted,
            "assembly": assembly_deleted,
            "total": total_deleted
        }
    def evaluate_logic_circuit(
        self, 
        game_id: str, 
        user_answer: int
    ) -> bool:
        """
        Evalúa la respuesta del usuario para un circuito lógico - SIMPLIFICADO.
        
        Args:
            game_id: Identificador del juego
            user_answer: Respuesta del usuario (0 o 1)
            
        Returns:
            True si se evaluó correctamente, False en caso contrario
        """
        try:
            updated_game = self.logic_diagram_service.evaluate_circuit(game_id, user_answer)
            return updated_game.get("answered", False)
        except Exception as e:
            logger.error(f"Error evaluando circuito lógico {game_id}: {str(e)}")
            return False
    
    def get_logic_circuit_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada del circuito para explicaciones.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Información del circuito o None si no existe
        """
        return self.logic_diagram_service.get_circuit_info(game_id)
    
    # Métodos mejorados para el juego de Ensamblador
    
    def evaluate_assembly_explanation(
        self, 
        game_id: str, 
        user_explanation: str
    ) -> bool:
        """
        Evalúa la explicación del usuario sobre el error de ensamblador.
        
        Args:
            game_id: Identificador del juego
            user_explanation: Explicación del usuario sobre el error
            
        Returns:
            True si se evaluó correctamente, False en caso contrario
        """
        try:
            updated_game = self.assembly_service.evaluate_explanation(game_id, user_explanation)
            return updated_game.get("answered", False)
        except Exception as e:
            logger.error(f"Error evaluando explicación de ensamblador {game_id}: {str(e)}")
            return False
    
    def get_assembly_feedback(self, game_id: str) -> Optional[str]:
        """
        Obtiene feedback específico para un juego de ensamblador.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Feedback específico o None si no existe
        """
        return self.assembly_service.generate_specific_feedback(game_id)
    
    # Métodos de utilidad para validación mejorada
    
    def validate_game_responses(self, game_type: str, responses: Dict[str, Any]) -> bool:
        """
        Valida que las respuestas de un juego cumplan con los criterios específicos.
        
        Args:
            game_type: Tipo de juego
            responses: Respuestas a validar
            
        Returns:
            True si las respuestas son válidas, False en caso contrario
        """
        try:
            if game_type == "hangman":
                # Validar que la adivinanza sea una sola letra o palabra
                guess = responses.get("guess", "")
                return isinstance(guess, str) and len(guess) >= 1 and guess.isalpha()
            
            elif game_type == "wordle":
                # Validar que la palabra sea exactamente de 5 letras
                word = responses.get("word", "")
                return isinstance(word, str) and len(word) == 5 and word.isalpha()
            
            elif game_type == "logic":
                # Validar que la respuesta sea 0 o 1
                answers = responses.get("answers", [])
                return (isinstance(answers, list) and 
                       len(answers) == 1 and 
                       answers[0] in [0, 1])
            
            elif game_type == "assembly":
                # Validar que haya una explicación con al menos 10 caracteres
                explanation = responses.get("explanation", "")
                return (isinstance(explanation, str) and 
                       len(explanation.strip()) >= 10)
            
            return False
            
        except Exception as e:
            logger.error(f"Error validando respuestas para {game_type}: {str(e)}")
            return False
    
    def get_game_progress(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el progreso actual de cualquier tipo de juego.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Información de progreso del juego o None si no existe
        """
        # Determinar tipo de juego por el prefijo del ID
        if game_id.startswith("hangman_"):
            game = self.get_hangman_game(game_id)
            if game:
                return {
                    "type": "hangman",
                    "completed": game.get("game_over", False),
                    "success": game.get("win", False),
                    "progress": f"{game.get('remaining_attempts', 0)} intentos restantes"
                }
        
        elif game_id.startswith("wordle_"):
            game = self.get_wordle_game(game_id)
            if game:
                attempts_used = len(game.get("attempts", []))
                max_attempts = game.get("max_attempts", 6)
                return {
                    "type": "wordle",
                    "completed": game.get("game_over", False),
                    "success": game.get("win", False),
                    "progress": f"{attempts_used}/{max_attempts} intentos usados"
                }
        
        elif game_id.startswith("logic_"):
            game = self.get_logic_game(game_id)
            if game:
                return {
                    "type": "logic",
                    "completed": game.get("answered", False),
                    "success": game.get("correct", False),
                    "progress": "Evaluación de circuito lógico"
                }
        
        elif game_id.startswith("assembly_"):
            game = self.get_assembly_game(game_id)
            if game:
                return {
                    "type": "assembly",
                    "completed": game.get("answered", False),
                    "success": game.get("evaluation_result", {}).get("correctness") in ["excellent", "good"],
                    "progress": "Análisis de código ensamblador"
                }
        
        return None
    
    def get_difficulty_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Obtiene estadísticas de juegos por dificultad.
        
        Returns:
            Estadísticas de juegos creados por tipo y dificultad
        """
        stats = {
            "easy": {"hangman": 0, "wordle": 0, "logic": 0, "assembly": 0},
            "medium": {"hangman": 0, "wordle": 0, "logic": 0, "assembly": 0},
            "hard": {"hangman": 0, "wordle": 0, "logic": 0, "assembly": 0}
        }
        
        # Contar juegos de hangman
        for game in self.hangman_service._games.values():
            difficulty = "medium"  # Por defecto, habría que agregar difficulty al juego
            if game.get("max_attempts", 6) >= 8:
                difficulty = "easy"
            elif game.get("max_attempts", 6) <= 5:
                difficulty = "hard"
            stats[difficulty]["hangman"] += 1
        
        # Contar juegos de wordle
        for game in self.wordle_service._games.values():
            difficulty = "medium"  # Por defecto
            if game.get("max_attempts", 6) >= 7:
                difficulty = "easy"
            elif game.get("max_attempts", 6) <= 5:
                difficulty = "hard"
            stats[difficulty]["wordle"] += 1
        
        # Contar juegos de logic
        for game in self.logic_diagram_service._games.values():
            difficulty = "medium"  # Se podría inferir de la complejidad del circuito
            stats[difficulty]["logic"] += 1
        
        # Contar juegos de assembly
        for game in self.assembly_service._games.values():
            difficulty = "medium"  # Se podría inferir de la cantidad de líneas
            stats[difficulty]["assembly"] += 1
        
        return stats
    
    def clean_old_games_by_type(self, game_type: str, max_age_hours: int = 24) -> int:
        """
        Limpia juegos antiguos de un tipo específico.
        
        Args:
            game_type: Tipo de juego a limpiar
            max_age_hours: Edad máxima en horas
            
        Returns:
            Número de juegos eliminados
        """
        if game_type == "hangman":
            return self.hangman_service.clean_old_games(max_age_hours)
        elif game_type == "wordle":
            return self.wordle_service.clean_old_games(max_age_hours)
        elif game_type == "logic":
            return self.logic_diagram_service.clean_old_games(max_age_hours)
        elif game_type == "assembly":
            return self.assembly_service.clean_old_games(max_age_hours)
        else:
            return 0

# Instancia global del servicio
games_service = GamesService()