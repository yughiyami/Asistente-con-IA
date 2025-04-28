"""
Servicio para el juego de Diagramas Lógicos.
Gestiona la lógica del juego y el estado de las partidas.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)


class LogicDiagramService:
    """
    Servicio para gestionar juegos de Diagramas Lógicos.
    
    Proporciona métodos para:
    - Crear nuevos juegos
    - Validar respuestas
    - Gestionar el estado de las partidas
    """
    
    def __init__(self):
        """Inicializa el servicio con almacenamiento en memoria."""
        # Diccionario para almacenar juegos {game_id: game_data}
        self._games: Dict[str, Dict[str, Any]] = {}
    
    def create_game(
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
            
        Raises:
            ValueError: Si los datos son inconsistentes
        """
        # Verificar consistencia de datos
        if len(input_values) != len(expected_output):
            raise ValueError("El número de conjuntos de entrada y salida debe coincidir")
        
        # Crear estado inicial del juego
        game_data = {
            "id": game_id,
            "pattern": pattern,
            "question": question,
            "input_values": input_values,
            "expected_output": expected_output,
            "answered": False,
            "user_answers": None,
            "correct": None,
            "explanation": None,
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar juego
        self._games[game_id] = game_data
        logger.info(f"Nuevo juego de Diagrama Lógico creado: {game_id}")
        
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
            logger.warning(f"Juego de Diagrama Lógico no encontrado: {game_id}")
            return None
        
        return game
    
    def validate_answers(
        self, 
        game_id: str, 
        user_answers: List[Union[int, str]]
    ) -> Dict[str, Any]:
        """
        Valida las respuestas propuestas por el usuario.
        
        Args:
            game_id: Identificador del juego
            user_answers: Lista de respuestas propuestas
            
        Returns:
            Estado actualizado del juego, incluyendo resultado de la validación
            
        Raises:
            ValueError: Si el juego no existe o ya fue contestado
        """
        # Obtener juego
        game = self._games.get(game_id)
        
        if not game:
            raise ValueError(f"Juego no encontrado: {game_id}")
        
        # Verificar si el juego ya fue contestado
        if game.get("answered", False):
            return game
        
        # Obtener datos actuales del juego
        expected_output = game["expected_output"]
        
        # Verificar número de respuestas
        if len(user_answers) != len(expected_output):
            raise ValueError(f"Número incorrecto de respuestas. Se esperaban {len(expected_output)}")
        
        # Normalizar respuestas para comparación
        normalized_expected = [str(val).strip().upper() for val in expected_output]
        normalized_user = [str(val).strip().upper() for val in user_answers]
        
        # Verificar respuestas
        all_correct = normalized_expected == normalized_user
        
        # Actualizar estado del juego
        game.update({
            "answered": True,
            "user_answers": user_answers,
            "correct": all_correct,
            "updated_at": datetime.now().isoformat()
        })
        
        # Registrar resultado
        logger.info(f"Juego de Diagrama Lógico {game_id} respondido. Correcto: {all_correct}")
        
        return game
    
    def add_explanation(self, game_id: str, explanation: str) -> bool:
        """
        Agrega una explicación educativa a un juego respondido.
        
        Args:
            game_id: Identificador del juego
            explanation: Explicación educativa sobre el patrón lógico
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        game = self._games.get(game_id)
        
        if not game or not game.get("answered"):
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
            logger.info(f"Juego de Diagrama Lógico eliminado: {game_id}")
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
            logger.info(f"Limpieza de juegos: {len(games_to_delete)} juegos de Diagrama Lógico eliminados")
        
        return len(games_to_delete)

# Instancia global del servicio
logic_diagram_service = LogicDiagramService()