"""
Servicio para manejo de documentos PDF.
Extrae y procesa contenido para contexto en chat.
"""

import os
import PyPDF2
from typing import List, Dict, Optional ,BinaryIO
import logging
from pathlib import Path
import hashlib
from datetime import datetime
import aiofiles
from fastapi import UploadFile, File

logger = logging.getLogger(__name__)


class DocumentService:
    """Servicio para procesamiento de documentos PDF"""
    
    def __init__(self, documents_path: str = "documents"):
        """
        Inicializa el servicio con la ruta de documentos.
        
        Args:
            documents_path: Ruta donde se almacenan los PDFs
        """
        self.documents_path = Path(documents_path)
        self.documents_path.mkdir(exist_ok=True)
        self.documents_metadata = {}
        self._load_existing_documents()

    def _load_existing_documents(self):
        """Carga metadatos de documentos existentes"""
        for pdf_file in self.documents_path.glob("*.pdf"):
            try:
                self._extract_metadata(pdf_file)
            except Exception as e:
                logger.error(f"Error cargando {pdf_file}: {str(e)}")
    
    def _extract_metadata(self, file_path: Path) -> Dict:
        """Extrae metadatos de un PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Extraer texto de las primeras páginas para topics
                sample_text = ""
                for i in range(min(3, num_pages)):
                    sample_text += pdf_reader.pages[i].extract_text()[:500]
                
                # Identificar topics basados en palabras clave
                topics = self._extract_topics(sample_text)
                
                metadata = {
                    "id": file_path.name,
                    "title": file_path.stem.replace("_", " ").title(),
                    "pages": num_pages,
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                    "topics": topics,
                    "upload_date": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    "content_preview": sample_text[:200]
                }
                
                self.documents_metadata[file_path.name] = metadata
                return metadata
                
        except Exception as e:
            logger.error(f"Error extrayendo metadatos de {file_path}: {str(e)}")
            return {}
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrae topics del texto"""
        text_lower = text.lower()
        
        topic_keywords = {
            "cpu": ["procesador", "cpu", "microprocesador", "processor"],
            "memoria": ["memoria", "ram", "rom", "memory", "cache"],
            "pipeline": ["pipeline", "segmentación", "etapas"],
            "registros": ["registro", "register", "acumulador"],
            "alu": ["alu", "arithmetic", "lógica", "unidad aritmética"],
            "buses": ["bus", "buses", "direcciones", "datos"],
            "instrucciones": ["instrucción", "instruction", "opcode"],
            "arquitectura": ["arquitectura", "von neumann", "harvard"],
            "cache": ["cache", "caché", "l1", "l2", "l3"],
            "ensamblador": ["assembly", "ensamblador", "asm", "assembler"]
        }
        
        found_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics if found_topics else ["general"]


    async def delete_document(self, document_id: str) -> bool:
        """
        Elimina un documento.
        
        Args:
            document_id: ID del documento a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        file_path = self.documents_path / document_id
        
        if file_path.exists():
            file_path.unlink()
            self.documents_metadata.pop(document_id, None)
            return True
        
        return False
    
    async def list_documents(self) -> List[Dict]:
        """
        Lista todos los documentos disponibles.
        
        Returns:
            Lista de documentos con metadatos
        """
        # Recargar metadatos por si hubo cambios
        self._load_existing_documents()
        
        return list(self.documents_metadata.values())
    
    async def get_document_content(self, document_ids: List[str]) -> Optional[str]:
        """
        Obtiene el contenido de los documentos especificados.
        
        Args:
            document_ids: Lista de IDs de documentos
            
        Returns:
            Contenido concatenado o None
        """
        if not document_ids:
            return None      
        content_parts = []
        
        for doc_id in document_ids:
            file_path = self.documents_path / doc_id
            
            if file_path.exists():
                try:
                    content = await self.extract_pdf_content(str(file_path))
                    if content:
                        doc_info = self.documents_metadata.get(doc_id, {})
                        title = doc_info.get("title", doc_id)
                        content_parts.append(f"=== {title} ===\n{content}")
                except Exception as e:
                    logger.error(f"Error extrayendo contenido de {doc_id}: {str(e)}")
        
        return "\n\n".join(content_parts) if content_parts else None
    
    async def get_document_for_gemini(self, document_id: str) -> Optional[Dict]:
        """
        Prepara un documento para ser usado con Gemini API.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Dict con path y mime_type para Gemini
        """
        file_path = self.documents_path / document_id
        
        if file_path.exists():
            return {
                "path": str(file_path.absolute()),
                "mime_type": "application/pdf"
            }
        
        return None
    
    async def extract_pdf_content(self, file_path: str) -> str:
        """
        Extrae texto de un archivo PDF.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Contenido extraído del PDF
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                # Limitar a 1000 páginas según límite de Gemini
                max_pages = min(len(pdf_reader.pages), 1000)
                
                for page_num in range(max_pages):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())
                
                return "\n".join(text_content)
                
        except Exception as e:
            logger.error(f"Error extrayendo contenido del PDF: {str(e)}")
            return ""
    
    async def search_documents(self, query: str) -> List[Dict]:
        """
        Busca documentos por query.
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de documentos que coinciden
        """
        query_lower = query.lower()
        matching_docs = []
        
        for doc_id, metadata in self.documents_metadata.items():
            # Buscar en título
            if query_lower in metadata.get("title", "").lower():
                matching_docs.append(metadata)
                continue
            
            # Buscar en topics
            if any(query_lower in topic.lower() for topic in metadata.get("topics", [])):
                matching_docs.append(metadata)
                continue
            
            # Buscar en preview de contenido
            if query_lower in metadata.get("content_preview", "").lower():
                matching_docs.append(metadata)
        
        return matching_docs


    async def upload_document(self, file: UploadFile) -> Dict:
        """
        Sube un nuevo documento PDF.
        
        Args:
            file: Archivo PDF subido
            
        Returns:
            Metadatos del documento subido
        """
        if not file.filename.endswith('.pdf'):
            raise ValueError("Solo se aceptan archivos PDF")
        
        # Validar tamaño (máximo 30MB según Gemini)
        file_size = 0
        contents = await file.read()
        file_size = len(contents) / (1024 * 1024)  # MB
        
        if file_size > 30:
            raise ValueError("El archivo excede el límite de 30MB")
        
        # Guardar archivo
        file_path = self.documents_path / file.filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # Extraer metadatos
        metadata = self._extract_metadata(file_path)
        
        return metadata

