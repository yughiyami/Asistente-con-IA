"""
Servicio para manejo de documentos PDF.
Extrae y procesa contenido para contexto en chat.
"""

import os
import PyPDF2
from typing import List, Dict, Optional
import logging
from pathlib import Path
import hashlib

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
        
        # Documentos de ejemplo predefinidos
        self._initialize_sample_documents()
    
    def _initialize_sample_documents(self):
        """Inicializa metadatos de documentos de ejemplo"""
        self.sample_documents = {
            "cpu_architecture.pdf": {
                "title": "Arquitectura de CPU Moderna",
                "pages": 45,
                "size_mb": 2.3,
                "topics": ["pipeline", "cache", "registros", "ALU"]
            },
            "memory_systems.pdf": {
                "title": "Sistemas de Memoria en Computadoras",
                "pages": 38,
                "size_mb": 1.8,
                "topics": ["RAM", "ROM", "cache", "memoria virtual"]
            },
            "instruction_sets.pdf": {
                "title": "Conjuntos de Instrucciones x86 y ARM",
                "pages": 52,
                "size_mb": 3.1,
                "topics": ["CISC", "RISC", "x86", "ARM", "instrucciones"]
            },
            "digital_logic.pdf": {
                "title": "Lógica Digital y Circuitos",
                "pages": 41,
                "size_mb": 2.5,
                "topics": ["compuertas", "flip-flops", "multiplexores", "ALU"]
            },
            "io_systems.pdf": {
                "title": "Sistemas de Entrada/Salida",
                "pages": 35,
                "size_mb": 1.9,
                "topics": ["buses", "interrupciones", "DMA", "periféricos"]
            }
        }
    
    async def list_documents(self) -> List[Dict]:
        """
        Lista todos los documentos disponibles.
        
        Returns:
            Lista de documentos con metadatos
        """
        documents = []
        
        # Por ahora retornamos documentos de ejemplo
        for doc_id, metadata in self.sample_documents.items():
            documents.append({
                "id": doc_id,
                "title": metadata["title"],
                "pages": metadata["pages"],
                "size_mb": metadata["size_mb"]
            })
        
        return documents
    
    async def get_document_content(
        self, 
        document_ids: List[str]
    ) -> Optional[str]:
        """
        Obtiene el contenido relevante de los documentos especificados.
        
        Args:
            document_ids: Lista de IDs de documentos
            
        Returns:
            Contenido concatenado o None
        """
        if not document_ids:
            return None
        
        # Por ahora, retornamos contenido simulado basado en los temas
        content_parts = []
        
        for doc_id in document_ids:
            if doc_id in self.sample_documents:
                doc_info = self.sample_documents[doc_id]
                content = self._generate_sample_content(doc_info)
                content_parts.append(f"=== {doc_info['title']} ===\n{content}")
        
        return "\n\n".join(content_parts) if content_parts else None
    
    def _generate_sample_content(self, doc_info: Dict) -> str:
        """
        Genera contenido de ejemplo basado en los temas del documento.
        
        Args:
            doc_info: Información del documento
            
        Returns:
            Contenido de ejemplo relevante
        """
        content_map = {
            "pipeline": """El pipeline es una técnica de paralelización que permite ejecutar múltiples 
            instrucciones simultáneamente dividiéndolas en etapas: IF (Instruction Fetch), 
            ID (Instruction Decode), EX (Execute), MEM (Memory Access), WB (Write Back).""",
            
            "cache": """La memoria caché es una memoria de alta velocidad que almacena copias de 
            datos frecuentemente utilizados. Se organiza en niveles: L1 (más rápida, menor capacidad), 
            L2 y L3 (más lenta, mayor capacidad). Utiliza principios de localidad temporal y espacial.""",
            
            "registros": """Los registros son elementos de memoria de alta velocidad dentro del CPU. 
            Incluyen registros de propósito general (RAX, RBX en x86), registros de estado (FLAGS), 
            y registros especiales como PC (Program Counter) y SP (Stack Pointer).""",
            
            "ALU": """La Unidad Aritmético-Lógica realiza operaciones matemáticas y lógicas. 
            Soporta operaciones como ADD, SUB, MUL, DIV, AND, OR, XOR, NOT. Es fundamental 
            para la ejecución de instrucciones.""",
            
            "RAM": """La RAM (Random Access Memory) es memoria volátil de acceso aleatorio. 
            Tipos incluyen SRAM (estática, rápida, cara) y DRAM (dinámica, más lenta, económica). 
            Se organiza en bancos y utiliza direccionamiento por filas y columnas.""",
            
            "memoria virtual": """La memoria virtual permite que los programas usen más memoria 
            de la físicamente disponible mediante paginación. Utiliza tablas de páginas para 
            traducir direcciones virtuales a físicas y maneja page faults.""",
            
            "CISC": """CISC (Complex Instruction Set Computer) tiene instrucciones complejas 
            que pueden realizar múltiples operaciones. Ejemplo: x86. Ventajas: código compacto. 
            Desventajas: decodificación compleja, dificulta pipeline.""",
            
            "RISC": """RISC (Reduced Instruction Set Computer) usa instrucciones simples y 
            uniformes. Ejemplo: ARM, MIPS. Ventajas: pipeline eficiente, decodificación simple. 
            Desventajas: programas más largos.""",
            
            "compuertas": """Las compuertas lógicas son los bloques básicos de los circuitos 
            digitales. Incluyen AND, OR, NOT, NAND, NOR, XOR, XNOR. Se combinan para crear 
            circuitos más complejos como sumadores y multiplexores.""",
            
            "buses": """Los buses son conjuntos de líneas que transportan información. 
            Tipos: bus de datos (transporta datos), bus de direcciones (especifica ubicaciones), 
            bus de control (señales de control). Ejemplos: PCI, USB, SATA.""",
            
            "interrupciones": """Las interrupciones permiten que dispositivos externos señalen 
            al CPU. Tipos: enmascarables y no enmascarables. El CPU guarda su estado, ejecuta 
            el ISR (Interrupt Service Routine) y luego restaura el estado.""",
            
            "DMA": """Direct Memory Access permite que periféricos accedan a memoria sin 
            intervención del CPU. Mejora el rendimiento en transferencias grandes. El controlador 
            DMA maneja las transferencias mientras el CPU ejecuta otras tareas."""
        }
        
        # Construir contenido basado en los temas del documento
        content_parts = []
        for topic in doc_info.get("topics", []):
            if topic in content_map:
                content_parts.append(content_map[topic])
        
        return "\n\n".join(content_parts)
    
    async def extract_pdf_content(self, file_path: str) -> str:
        """
        Extrae texto de un archivo PDF real.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Contenido extraído del PDF
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())
                
                return "\n".join(text_content)
                
        except Exception as e:
            logger.error(f"Error extrayendo contenido del PDF: {str(e)}")
            return ""
    
    def get_document_hash(self, file_path: str) -> str:
        """
        Calcula el hash de un documento para identificación única.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Hash SHA-256 del archivo
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()