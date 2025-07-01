"""
Servicio para manejo de Redis.
Gestiona sesiones, caché y estado de juegos.
"""

import redis
import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Servicio para interactuar con Redis"""
    
    def __init__(self):
        """Inicializa la conexión a Redis"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True
            )
            # Verificar conexión
            self.redis_client.ping()
            logger.info("Conexión a Redis establecida")
        except Exception as e:
            logger.error(f"Error conectando a Redis: {str(e)}")
            raise
    
    # Métodos para manejo de sesiones de chat
    async def create_chat_session(self) -> str:
        """
        Crea una nueva sesión de chat.
        
        Returns:
            ID de la sesión creada
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
        
        key = f"chat:session:{session_id}"
        self.redis_client.setex(
            key,
            timedelta(minutes=settings.session_expire_minutes),
            json.dumps(session_data)
        )
        
        return session_id
    
    async def get_chat_session(self, session_id: str) -> Optional[Dict]:
        """
        Obtiene los datos de una sesión de chat.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Datos de la sesión o None si no existe
        """
        key = f"chat:session:{session_id}"
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def add_chat_message(
        self, 
        session_id: str, 
        role: str, 
        content: str
    ) -> bool:
        """
        Agrega un mensaje a la sesión de chat.
        
        Args:
            session_id: ID de la sesión
            role: Rol del mensaje (user/assistant)
            content: Contenido del mensaje
            
        Returns:
            True si se agregó correctamente
        """
        session = await self.get_chat_session(session_id)
        if not session:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session["messages"].append(message)
        session["updated_at"] = datetime.utcnow().isoformat()
        
        key = f"chat:session:{session_id}"
        self.redis_client.setex(
            key,
            timedelta(minutes=settings.session_expire_minutes),
            json.dumps(session)
        )
        
        return True
    
    # Métodos para manejo de exámenes
    async def save_exam(self, exam_id: str, exam_data: Dict) -> bool:
        """
        Guarda los datos de un examen con respuestas correctas.
        
        Args:
            exam_id: ID del examen
            exam_data: Datos completos del examen
            
        Returns:
            True si se guardó correctamente
        """
        key = f"exam:{exam_id}"
        # Guardar por 24 horas
        self.redis_client.setex(
            key,
            timedelta(hours=24),
            json.dumps(exam_data)
        )
        return True
    
    async def get_exam(self, exam_id: str) -> Optional[Dict]:
        """
        Obtiene los datos de un examen.
        
        Args:
            exam_id: ID del examen
            
        Returns:
            Datos del examen o None
        """
        key = f"exam:{exam_id}"
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    # Métodos para manejo de juegos
    async def save_game_state(
        self, 
        game_id: str, 
        game_type: str,
        state: Dict
    ) -> bool:
        """
        Guarda el estado de un juego.
        
        Args:
            game_id: ID del juego
            game_type: Tipo de juego
            state: Estado completo del juego
            
        Returns:
            True si se guardó correctamente
        """
        key = f"game:{game_type}:{game_id}"
        # Guardar por 2 horas
        self.redis_client.setex(
            key,
            timedelta(hours=2),
            json.dumps(state)
        )
        return True
    
    async def get_game_state(
        self, 
        game_id: str, 
        game_type: str
    ) -> Optional[Dict]:
        """
        Obtiene el estado de un juego.
        
        Args:
            game_id: ID del juego
            game_type: Tipo de juego
            
        Returns:
            Estado del juego o None
        """
        key = f"game:{game_type}:{game_id}"
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def update_game_state(
        self, 
        game_id: str, 
        game_type: str,
        updates: Dict
    ) -> bool:
        """
        Actualiza parcialmente el estado de un juego.
        
        Args:
            game_id: ID del juego
            game_type: Tipo de juego
            updates: Actualizaciones a aplicar
            
        Returns:
            True si se actualizó correctamente
        """
        state = await self.get_game_state(game_id, game_type)
        if not state:
            return False
        
        state.update(updates)
        state["updated_at"] = datetime.utcnow().isoformat()
        
        return await self.save_game_state(game_id, game_type, state)
    
    # Métodos para caché de documentos
    async def cache_document_content(
        self, 
        doc_id: str, 
        content: str,
        expire_hours: int = 24
    ) -> bool:
        """
        Cachea el contenido de un documento.
        
        Args:
            doc_id: ID del documento
            content: Contenido a cachear
            expire_hours: Horas antes de expirar
            
        Returns:
            True si se cacheó correctamente
        """
        key = f"doc:content:{doc_id}"
        self.redis_client.setex(
            key,
            timedelta(hours=expire_hours),
            content
        )
        return True
    
    async def get_cached_document(self, doc_id: str) -> Optional[str]:
        """
        Obtiene el contenido cacheado de un documento.
        
        Args:
            doc_id: ID del documento
            
        Returns:
            Contenido del documento o None
        """
        key = f"doc:content:{doc_id}"
        return self.redis_client.get(key)
    
    # Métodos de utilidad
    async def increment_counter(
        self, 
        counter_name: str, 
        expire_hours: int = 24
    ) -> int:
        """
        Incrementa un contador.
        
        Args:
            counter_name: Nombre del contador
            expire_hours: Horas antes de reiniciar
            
        Returns:
            Valor actual del contador
        """
        key = f"counter:{counter_name}"
        value = self.redis_client.incr(key)
        
        if value == 1:
            # Establecer expiración solo en el primer incremento
            self.redis_client.expire(key, timedelta(hours=expire_hours))
        
        return value
    
    async def clear_session(self, session_type: str, session_id: str) -> bool:
        """
        Elimina una sesión específica.
        
        Args:
            session_type: Tipo de sesión (chat, exam, game)
            session_id: ID de la sesión
            
        Returns:
            True si se eliminó correctamente
        """
        key = f"{session_type}:{session_id}"
        return bool(self.redis_client.delete(key))