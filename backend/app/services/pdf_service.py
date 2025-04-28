"""
Servicio para la gestión de PDFs y extracción de contenido.
Proporciona funcionalidades para acceder y procesar documentos del curso.
"""

import os
import logging
from typing import Dict, List, Optional, Set
from pathlib import Path

# Importaciones para procesamiento de PDFs
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# Importación de configuración
from app.config import settings

# Configurar logger
logger = logging.getLogger(__name__)

# Descargar recursos de NLTK necesarios (al iniciar el servicio)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"No se pudieron descargar recursos NLTK: {str(e)}")


class PDFService:
    """
    Servicio para gestionar y extraer contenido de documentos PDF.
    
    Esta clase proporciona métodos para:
    - Listar documentos disponibles
    - Extraer texto completo de documentos
    - Buscar contenido relevante para una consulta
    - Extraer metadatos de documentos
    """
    
    def __init__(self, pdf_library_path: Optional[str] = None):
        """
        Inicializa el servicio de PDFs.
        
        Args:
            pdf_library_path: Ruta a la biblioteca de PDFs (opcional, usa configuración por defecto)
        """
        self.pdf_library_path = pdf_library_path or settings.PDF_LIBRARY_PATH
        self.document_cache: Dict[str, Dict] = {}  # Caché para contenido de documentos
        
        # Asegurar que la carpeta de PDFs existe
        os.makedirs(self.pdf_library_path, exist_ok=True)
    
    def list_available_documents(self) -> List[Dict[str, str]]:
        """
        Lista todos los documentos PDF disponibles en la biblioteca.
        
        Returns:
            Lista de diccionarios con información básica de cada documento
        """
        documents = []
        
        pdf_path = Path(self.pdf_library_path)
        for file_path in pdf_path.glob("**/*.pdf"):
            try:
                # Extraer información básica
                doc_id = str(file_path.relative_to(pdf_path))
                
                # Si el documento está en caché, usar esa información
                if doc_id in self.document_cache:
                    documents.append({
                        "id": doc_id,
                        "title": self.document_cache[doc_id].get("title", file_path.stem),
                        "path": str(file_path)
                    })
                    continue
                
                # Si no está en caché, extraer título del documento
                doc = fitz.open(file_path)
                metadata = doc.metadata
                title = metadata.get("title", file_path.stem)
                
                documents.append({
                    "id": doc_id,
                    "title": title,
                    "path": str(file_path)
                })
                
            except Exception as e:
                logger.error(f"Error al procesar documento {file_path}: {str(e)}")
        
        return sorted(documents, key=lambda x: x["title"])
    
    async def get_document_content(self, doc_id: str) -> Dict[str, any]:
        """
        Extrae el contenido completo de un documento PDF.
        
        Args:
            doc_id: Identificador del documento
            
        Returns:
            Diccionario con el contenido y metadatos del documento
            
        Raises:
            FileNotFoundError: Si el documento no existe
        """
        # Verificar si el documento está en caché
        if doc_id in self.document_cache:
            return self.document_cache[doc_id]
        
        # Construir ruta al documento
        doc_path = os.path.join(self.pdf_library_path, doc_id)
        
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Documento no encontrado: {doc_id}")
        
        try:
            # Abrir el documento con PyMuPDF
            doc = fitz.open(doc_path)
            
            # Extraer metadatos
            metadata = doc.metadata
            
            # Extraer texto completo
            full_text = ""
            toc = []  # Tabla de contenidos
            
            # Extraer tabla de contenidos si está disponible
            toc_data = doc.get_toc()
            if toc_data:
                for t in toc_data:
                    level, title, page = t
                    toc.append({"level": level, "title": title, "page": page})
            
            # Extraer texto por páginas
            pages_text = []
            for page_num, page in enumerate(doc):
                text = page.get_text()
                pages_text.append(text)
                full_text += text + "\n\n"
            
            # Construir resultado
            result = {
                "id": doc_id,
                "title": metadata.get("title", os.path.basename(doc_id)),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "full_text": full_text,
                "pages_text": pages_text,
                "toc": toc,
                "page_count": len(doc)
            }
            
            # Guardar en caché
            self.document_cache[doc_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error al extraer contenido de {doc_id}: {str(e)}")
            raise
    
    async def search_relevant_content(
        self, 
        query: str, 
        doc_ids: Optional[List[str]] = None,
        max_results: int = 5
    ) -> List[Dict[str, any]]:
        """
        Busca contenido relevante para una consulta en los documentos especificados.
        
        Args:
            query: Consulta o pregunta del usuario
            doc_ids: Lista de IDs de documentos donde buscar (opcional, usa todos si es None)
            max_results: Número máximo de resultados a devolver
            
        Returns:
            Lista de fragmentos relevantes con metadatos
        """
        # Si no se especifican documentos, usar todos los disponibles
        if not doc_ids:
            documents = self.list_available_documents()
            doc_ids = [doc["id"] for doc in documents]
        
        results = []
        
        # Preprocesar la consulta
        query_words = set(self._preprocess_text(query))
        
        for doc_id in doc_ids:
            try:
                # Obtener contenido del documento
                doc_content = await self.get_document_content(doc_id)
                
                # Dividir en párrafos y oraciones
                paragraphs = doc_content["full_text"].split("\n\n")
                
                for para_idx, paragraph in enumerate(paragraphs):
                    if not paragraph.strip():
                        continue
                    
                    # Dividir en oraciones
                    sentences = sent_tokenize(paragraph)
                    
                    # Si el párrafo es muy corto, usarlo completo
                    if len(sentences) <= 3:
                        relevance_score = self._calculate_relevance(paragraph, query_words)
                        if relevance_score > 0:
                            results.append({
                                "doc_id": doc_id,
                                "doc_title": doc_content["title"],
                                "content": paragraph,
                                "score": relevance_score
                            })
                    else:
                        # Procesar grupos de oraciones (ventana deslizante)
                        window_size = 3
                        for i in range(len(sentences) - window_size + 1):
                            content = " ".join(sentences[i:i+window_size])
                            relevance_score = self._calculate_relevance(content, query_words)
                            
                            if relevance_score > 0:
                                results.append({
                                    "doc_id": doc_id,
                                    "doc_title": doc_content["title"],
                                    "content": content,
                                    "score": relevance_score
                                })
            
            except Exception as e:
                logger.error(f"Error al buscar en documento {doc_id}: {str(e)}")
                continue
        
        # Ordenar por relevancia y limitar resultados
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocesa el texto para búsqueda (tokenización y eliminación de stopwords).
        
        Args:
            text: Texto a preprocesar
            
        Returns:
            Lista de palabras procesadas
        """
        # Convertir a minúsculas
        text = text.lower()
        
        # Tokenizar
        words = nltk.word_tokenize(text)
        
        # Eliminar stopwords
        stop_words = set(stopwords.words('spanish') + stopwords.words('english'))
        words = [word for word in words if word.isalnum() and word not in stop_words]
        
        return words
    
    def _calculate_relevance(self, text: str, query_words: Set[str]) -> float:
        """
        Calcula la relevancia de un fragmento de texto para una consulta.
        
        Args:
            text: Fragmento de texto
            query_words: Conjunto de palabras de la consulta
            
        Returns:
            Puntuación de relevancia
        """
        # Preprocesar el texto
        text_words = set(self._preprocess_text(text))
        
        # Calcular intersección
        common_words = text_words.intersection(query_words)
        
        if not common_words:
            return 0
        
        # Calcular puntuación basada en palabras en común y densidad
        score = len(common_words) / len(query_words)
        density = len(common_words) / len(text_words) if text_words else 0
        
        # Combinar puntuaciones
        return 0.7 * score + 0.3 * density


# Instancia global del servicio
pdf_service = PDFService()