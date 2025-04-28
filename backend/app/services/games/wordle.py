"""
Servicio para el juego de Wordle.
Gestiona la lógica del juego y el estado de las partidas.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# Configurar logger
logger = logging.getLogger(__name__)


class LetterResult(str, Enum):
    """Resultado de cada letra en Wordle."""
    CORRECT = "correct"  # Letra correcta en posición correcta
    PRESENT = "present"  # Letra correcta en posición incorrecta
    ABSENT = "absent"    # Letra no presente en la palabra


class WordleService:
    """
    Servicio para gestionar juegos de Wordle.
    
    Proporciona métodos para:
    - Crear nuevos juegos
    - Procesar adivinanzas
    - Gestionar el estado de las partidas
    """
    
    def __init__(self):
        """Inicializa el servicio con almacenamiento en memoria."""
        # Diccionario para almacenar juegos {game_id: game_data}
        self._games: Dict[str, Dict[str, Any]] = {}
    
    def create_game(
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
            
        Raises:
            ValueError: Si la palabra no tiene exactamente 5 letras
        """
        # Preparar palabra (convertir a mayúsculas)
        word = word.upper()
        
        # Verificar longitud de la palabra
        if len(word) != 5:
            raise ValueError("La palabra debe tener exactamente 5 letras")
        
        # Crear estado inicial del juego
        game_data = {
            "id": game_id,
            "word": word,
            "topic_hint": topic_hint,
            "max_attempts": max_attempts,
            "attempts": [],  # Lista de palabras intentadas
            "results": [],   # Resultados de cada intento
            "game_over": False,
            "win": False,
            "explanation": None,  # Explicación del término (se agrega al terminar)
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar juego
        self._games[game_id] = game_data
        logger.info(f"Nuevo juego de Wordle creado: {game_id}")
        
        return game_data
    
    def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un juego por su ID.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Datos del juego o None si no existe
        """
        game = self._games.get(game_id)
        
        if not game:
            logger.warning(f"Juego de Wordle no encontrado: {game_id}")
            return None
        
        return game
    
    def process_guess(self, game_id: str, guess: str) -> Dict[str, Any]:
        """
        Procesa una adivinanza en el juego.
        
        Args:
            game_id: Identificador del juego
            guess: Palabra adivinada (debe tener 5 letras)
            
        Returns:
            Estado actualizado del juego, incluyendo resultado de la adivinanza
            
        Raises:
            ValueError: Si el juego no existe, ya terminó, o la palabra no tiene 5 letras
        """
        # Obtener juego
        game = self._games.get(game_id)
        
        if not game:
            raise ValueError(f"Juego no encontrado: {game_id}")
        
        # Verificar si el juego ya terminó
        if game.get("game_over", False):
            return game
        
        # Normalizar adivinanza (convertir a mayúsculas)
        guess = guess.upper()
        
        # Verificar longitud de la palabra
        if len(guess) != 5:
            raise ValueError("La palabra debe tener exactamente 5 letras")
        
        # Obtener datos actuales del juego
        word = game["word"]
        attempts = game["attempts"]
        results = game["results"]
        max_attempts = game["max_attempts"]
        
        # Calcular resultados para cada letra
        letter_results = []
        
        # Primero marcar las letras correctas en posición correcta
        word_chars = list(word)
        for i, char in enumerate(guess):
            if i < len(word) and char == word[i]:
                letter_results.append(LetterResult.CORRECT)
                word_chars[i] = "*"  # Marcar como usada
            else:
                letter_results.append(None)  # Temporal, se completará después
        
        # Luego marcar las letras presentes pero en posición incorrecta
        for i, char in enumerate(guess):
            if letter_results[i] is None:  # Solo procesar posiciones aún sin resultado
                if char in word_chars:
                    letter_results[i] = LetterResult.PRESENT
                    word_chars[word_chars.index(char)] = "*"  # Marcar como usada
                else:
                    letter_results[i] = LetterResult.ABSENT
        
        # Actualizar el estado del juego
        attempts.append(guess)
        results.append(letter_results)
        
        # Verificar si el juego ha terminado
        attempt_number = len(attempts)
        win = guess == word
        game_over = win or attempt_number >= max_attempts
        
        # Actualizar estado del juego
        game.update({
            "attempts": attempts,
            "results": results,
            "game_over": game_over,
            "win": win,
            "updated_at": datetime.now().isoformat()
        })
        
        # Registrar resultado
        if game_over:
            logger.info(f"Juego de Wordle {game_id} terminado. Victoria: {win}")
        
        return game
    
    def add_explanation(self, game_id: str, explanation: str) -> bool:
        """
        Agrega una explicación educativa a un juego finalizado.
        
        Args:
            game_id: Identificador del juego
            explanation: Explicación educativa sobre el término
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        game = self._games.get(game_id)
        
        if not game or not game.get("game_over"):
            return False
        
        game["explanation"] = explanation
        return True
    
    def delete_game(self, game_id: str) -> bool:
        """
        Elimina un juego del almacenamiento.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if game_id in self._games:
            del self._games[game_id]
            logger.info(f"Juego de Wordle eliminado: {game_id}")
            return True
        
        logger.warning(f"Intento de eliminar juego inexistente: {game_id}")
        return False
    
    def clean_old_games(self, max_age_hours: int = 24) -> int:
        """
        Elimina juegos antiguos para liberar memoria.
        
        Args:
            max_age_hours: Edad máxima en horas para conservar juegos
            
        Returns:
            Número de juegos eliminados
        """
        import datetime as dt
        
        now = dt.datetime.now()
        cutoff = now - dt.timedelta(hours=max_age_hours)
        cutoff_iso = cutoff.isoformat()
        
        games_to_delete = []
        
        for game_id, game_data in self._games.items():
            created_at = game_data.get("created_at", "")
            
            if created_at < cutoff_iso:
                games_to_delete.append(game_id)
        
        # Eliminar juegos antiguos
        for game_id in games_to_delete:
            del self._games[game_id]
        
        if games_to_delete:
            logger.info(f"Limpieza de juegos: {len(games_to_delete)} juegos de Wordle eliminados")
        
        return len(games_to_delete)

# Instancia global del servicio
wordle_service = WordleService()