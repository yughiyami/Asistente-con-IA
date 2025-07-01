"""
Utilidades compartidas para toda la aplicación.
Funciones auxiliares y helpers comunes.
"""

import hashlib
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import string


def generate_unique_id(prefix: str = "") -> str:
    """
    Genera un ID único con prefijo opcional.
    
    Args:
        prefix: Prefijo para el ID
        
    Returns:
        ID único con formato: prefix_timestamp_random
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    if prefix:
        return f"{prefix}_{timestamp}_{random_part}"
    return f"{timestamp}_{random_part}"


def sanitize_text(text: str) -> str:
    """
    Limpia y sanitiza texto para uso seguro.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto sanitizado
    """
    # Remover caracteres de control
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Normalizar espacios en blanco
    text = ' '.join(text.split())
    
    return text.strip()


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extrae palabras clave de un texto.
    
    Args:
        text: Texto del cual extraer palabras
        min_length: Longitud mínima de las palabras
        
    Returns:
        Lista de palabras clave únicas
    """
    # Convertir a minúsculas y extraer palabras
    words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
    
    # Filtrar palabras comunes en español
    stop_words = {
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
        'no', 'haber', 'por', 'con', 'su', 'para', 'como', 'estar',
        'tener', 'le', 'lo', 'todo', 'pero', 'más', 'hacer', 'o',
        'poder', 'decir', 'este', 'ir', 'otro', 'ese', 'la', 'si',
        'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'muy', 'sin',
        'vez', 'mucho', 'saber', 'qué', 'sobre', 'mi', 'alguno', 'mismo'
    }
    
    # Filtrar por longitud y palabras vacías
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Retornar palabras únicas manteniendo el orden
    seen = set()
    unique_keywords = []
    for word in keywords:
        if word not in seen:
            seen.add(word)
            unique_keywords.append(word)
    
    return unique_keywords


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calcula la similitud entre dos textos usando el coeficiente de Jaccard.
    
    Args:
        text1: Primer texto
        text2: Segundo texto
        
    Returns:
        Puntuación de similitud entre 0 y 1
    """
    # Extraer palabras clave de ambos textos
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 and not keywords2:
        return 1.0
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calcular coeficiente de Jaccard
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    return len(intersection) / len(union)


def format_time_duration(seconds: int) -> str:
    """
    Formatea una duración en segundos a formato legible.
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        Duración formateada (ej: "2h 30m", "45m", "30s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes > 0:
        return f"{hours}h {remaining_minutes}m"
    return f"{hours}h"


def paginate_list(items: List[Any], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    Pagina una lista de elementos.
    
    Args:
        items: Lista de elementos
        page: Número de página (empezando en 1)
        page_size: Tamaño de página
        
    Returns:
        Diccionario con items paginados e información de paginación
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    # Validar página
    page = max(1, min(page, total_pages))
    
    start_index = (page - 1) * page_size
    end_index = min(start_index + page_size, total_items)
    
    return {
        "items": items[start_index:end_index],
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages
        }
    }


def hash_string(text: str) -> str:
    """
    Genera un hash SHA-256 de un texto.
    
    Args:
        text: Texto a hashear
        
    Returns:
        Hash hexadecimal del texto
    """
    return hashlib.sha256(text.encode()).hexdigest()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    # Truncar considerando el sufijo
    truncate_at = max_length - len(suffix)
    
    # Intentar truncar en un espacio para no cortar palabras
    last_space = text.rfind(' ', 0, truncate_at)
    if last_space > truncate_at * 0.8:  # Si hay un espacio cercano
        truncate_at = last_space
    
    return text[:truncate_at].rstrip() + suffix


def validate_email(email: str) -> bool:
    """
    Valida formato básico de email.
    
    Args:
        email: Email a validar
        
    Returns:
        True si el formato es válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def get_file_extension(filename: str) -> str:
    """
    Obtiene la extensión de un archivo.
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Extensión sin el punto
    """
    parts = filename.rsplit('.', 1)
    if len(parts) > 1:
        return parts[1].lower()
    return ""


def is_valid_pdf(filename: str) -> bool:
    """
    Verifica si un archivo es un PDF válido por su extensión.
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        True si es un PDF
    """
    return get_file_extension(filename) == 'pdf'


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calcula el tiempo estimado de lectura en minutos.
    
    Args:
        text: Texto a leer
        words_per_minute: Velocidad de lectura promedio
        
    Returns:
        Tiempo estimado en minutos
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    
    # Redondear hacia arriba
    return max(1, int(minutes + 0.5))


def normalize_spanish_text(text: str) -> str:
    """
    Normaliza texto en español removiendo acentos para búsquedas.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto sin acentos
    """
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N'
    }
    
    for accented, unaccented in replacements.items():
        text = text.replace(accented, unaccented)
    
    return text