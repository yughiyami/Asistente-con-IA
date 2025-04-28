"""
Servicio para el juego de Ahorcado (Hangman).
Gestiona la lógica del juego y el estado de las partidas.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)


class HangmanService:
    """
    Servicio para gestionar juegos de Ahorcado.
    
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
        clue: str, 
        argument: str,
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
        # Preparar palabra (convertir a mayúsculas)
        word = word.upper()
        
        # Crear estado inicial del juego
        game_data = {
            "id": game_id,
            "word": word,
            "clue": clue,
            "argument": argument,
            "max_attempts": max_attempts,
            "remaining_attempts": max_attempts,
            "current_word": "_ " * len(word),
            "guessed_letters": [],
            "guessed_words": [],
            "game_over": False,
            "win": False,
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar juego
        self._games[game_id] = game_data
        logger.info(f"Nuevo juego de Ahorcado creado: {game_id}")
        
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
            logger.warning(f"Juego de Ahorcado no encontrado: {game_id}")
            return None
        
        return game
    
    def process_guess(self, game_id: str, guess: str) -> Dict[str, Any]:
        """
        Procesa una adivinanza en el juego.
        
        Args:
            game_id: Identificador del juego
            guess: Letra o palabra adivinada
            
        Returns:
            Estado actualizado del juego
            
        Raises:
            ValueError: Si el juego no existe o ya terminó
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
        
        # Obtener datos actuales del juego
        word = game["word"]
        current_word = game["current_word"].split()
        remaining_attempts = game["remaining_attempts"]
        guessed_letters = game["guessed_letters"]
        guessed_words = game["guessed_words"]
        
        # Determinar si es adivinanza de letra o palabra completa
        is_correct = False
        
        if len(guess) == 1:  # Es una letra
            # Verificar si la letra ya fue adivinada
            if guess in guessed_letters:
                return game  # No penalizar por repetir letra
            
            # Agregar a letras adivinadas
            guessed_letters.append(guess)
            
            # Verificar si la letra está en la palabra
            if guess in word:
                is_correct = True
                
                # Actualizar la palabra parcialmente revelada
                for i, char in enumerate(word):
                    if char == guess:
                        current_word[i] = char
            else:
                # Reducir intentos restantes
                remaining_attempts -= 1
                
        else:  # Es una palabra completa
            # Verificar si la palabra ya fue adivinada
            if guess in guessed_words:
                return game  # No penalizar por repetir palabra
            
            # Agregar a palabras adivinadas
            guessed_words.append(guess)
            
            # Verificar si la palabra es correcta
            if guess == word:
                is_correct = True
                
                # Revelar toda la palabra
                current_word = list(word)
            else:
                # Reducir intentos restantes
                remaining_attempts -= 1
        
        # Convertir lista actual a string con espacios
        current_word_str = " ".join(current_word)
        
        # Verificar si el juego ha terminado
        game_over = remaining_attempts <= 0 or "_" not in current_word_str
        win = "_" not in current_word_str
        
        # Actualizar estado del juego
        game.update({
            "current_word": current_word_str,
            "remaining_attempts": remaining_attempts,
            "guessed_letters": guessed_letters,
            "guessed_words": guessed_words,
            "game_over": game_over,
            "win": win,
            "last_guess": guess,
            "last_guess_correct": is_correct,
            "updated_at": datetime.now().isoformat()
        })
        
        # Registrar resultado
        if game_over:
            logger.info(f"Juego de Ahorcado {game_id} terminado. Victoria: {win}")
        
        return game
    
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
            logger.info(f"Juego de Ahorcado eliminado: {game_id}")
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
            logger.info(f"Limpieza de juegos: {len(games_to_delete)} juegos de Ahorcado eliminados")
        
        return len(games_to_delete)

# Instancia global del servicio
hangman_service = HangmanService()