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
    
    def update_logic_game_explanation(self, game_id: str, explanation: str) -> bool:
        """
        Agrega una explicación educativa a un juego de Diagrama Lógico.
        
        Args:
            game_id: Identificador del juego
            explanation: Explicación educativa sobre el patrón lógico
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        return self.logic_diagram_service.add_explanation(game_id, explanation)
    
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
    
    def update_assembly_game_explanation(self, game_id: str, explanation: str) -> bool:
        """
        Agrega una explicación educativa a un juego de Ensamblador.
        
        Args:
            game_id: Identificador del juego
            explanation: Explicación educativa sobre la solución correcta
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        return self.assembly_service.add_explanation(game_id, explanation)
    
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


# Instancia global del servicio
games_service = GamesService()