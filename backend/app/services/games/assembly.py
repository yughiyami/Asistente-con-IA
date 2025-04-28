"""
Servicio para el juego de Ensamblador.
Gestiona la lógica del juego y el estado de las partidas.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)


class AssemblyService:
    """
    Servicio para gestionar juegos de Ensamblador.
    
    Proporciona métodos para:
    - Crear nuevos juegos
    - Validar soluciones propuestas
    - Gestionar el estado de las partidas
    """
    
    def __init__(self):
        """Inicializa el servicio con almacenamiento en memoria."""
        # Diccionario para almacenar juegos {game_id: game_data}
        self._games: Dict[str, Dict[str, Any]] = {}
    
    def create_game(
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
        # Crear estado inicial del juego
        game_data = {
            "id": game_id,
            "code": code,
            "architecture": architecture,
            "expected_behavior": expected_behavior,
            "hint": hint,
            "solution": solution,
            "answered": False,
            "user_solution": None,
            "correct": None,
            "explanation": None,
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar juego
        self._games[game_id] = game_data
        logger.info(f"Nuevo juego de Ensamblador creado: {game_id}, Arquitectura: {architecture}")
        
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
            logger.warning(f"Juego de Ensamblador no encontrado: {game_id}")
            return None
        
        return game
    
    def validate_solution(
        self, 
        game_id: str, 
        corrected_code: str,
        explanation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida la solución propuesta por el usuario.
        
        Args:
            game_id: Identificador del juego
            corrected_code: Código corregido
            explanation: Explicación de la corrección (opcional)
            
        Returns:
            Estado actualizado del juego, incluyendo resultado de la validación
            
        Raises:
            ValueError: Si el juego no existe o ya fue respondido
        """
        # Obtener juego
        game = self._games.get(game_id)
        
        if not game:
            raise ValueError(f"Juego no encontrado: {game_id}")
        
        # Verificar si el juego ya fue respondido
        if game.get("answered", False):
            return game
        
        # Obtener datos actuales del juego
        solution = game["solution"]
        
        # Verificar si la solución está presente en el código corregido
        is_correct = solution.strip() in corrected_code
        
        # Actualizar estado del juego
        game.update({
            "answered": True,
            "user_solution": corrected_code,
            "user_explanation": explanation,
            "correct": is_correct,
            "updated_at": datetime.now().isoformat()
        })
        
        # Registrar resultado
        logger.info(f"Juego de Ensamblador {game_id} respondido. Correcto: {is_correct}")
        
        return game
    
    def add_explanation(self, game_id: str, explanation: str) -> bool:
        """
        Agrega una explicación educativa a un juego respondido.
        
        Args:
            game_id: Identificador del juego
            explanation: Explicación educativa sobre la solución correcta
            
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
            logger.info(f"Juego de Ensamblador eliminado: {game_id}")
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
            logger.info(f"Limpieza de juegos: {len(games_to_delete)} juegos de Ensamblador eliminados")
        
        return len(games_to_delete)

# Instancia global del servicio
assembly_service = AssemblyService()