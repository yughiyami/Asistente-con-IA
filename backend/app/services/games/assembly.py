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
        self._games: Dict[str, Dict[str, Any]] = {}
        
        # Tipos de errores clasificados por dificultad
        self._error_types = {
            "easy": {
                "syntax": "Errores de sintaxis básicos (registros mal escritos, comas faltantes)",
                "instruction": "Instrucciones incorrectas (ADD en lugar de SUB)",
                "operand": "Operandos intercambiados o incorrectos"
            },
            "medium": {
                "logic": "Errores lógicos (condiciones incorrectas, bucles infinitos)",
                "addressing": "Modos de direccionamiento incorrectos",
                "register": "Uso incorrecto de registros específicos"
            },
            "hard": {
                "semantic": "Errores semánticos (violación de convenciones)",
                "optimization": "Código ineficiente o subóptimo",
                "architecture": "Uso incorrecto de características específicas de arquitectura"
            }
        }
        
        # Patrones de código errado por arquitectura
        self._code_templates = {
            "MIPS_basic": {
                "easy": [
                    {
                        "code": "add $t0, $t1, $t2\nsub $t0, $t1, $t3\nmove $a0, $t0",
                        "error": "sub debería usar $t2 en lugar de $t3",
                        "concept": "Operaciones aritméticas básicas"
                    },
                    {
                        "code": "li $t0, 10\nli $t1, 5\nadd $t2, $t0, $t1\nsw $t2, 0($sp)",
                        "error": "sw debería usar offset correcto o inicializar $sp",
                        "concept": "Carga de inmediatos y almacenamiento"
                    }
                ]
            },
            "x86": {
                "medium": [
                    {
                        "code": "mov eax, 10\nmov ebx, 5\nadd eax, ebx\nmov [esp], eax",
                        "error": "mov [esp] puede causar problemas de stack, debería usar push",
                        "concept": "Manejo de stack en x86"
                    }
                ]
            }
        }
    
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
        Crea un nuevo juego de Ensamblador con código que contiene errores.
        
        Args:
            game_id: Identificador único del juego
            code: Código en ensamblador CON ERRORES
            architecture: Arquitectura del ensamblador
            expected_behavior: Lo que DEBERÍA hacer el código
            hint: Pista sobre dónde buscar el error
            solution: Explicación interna del error para evaluación
            
        Returns:
            Datos del juego creado
        """
        # Analizar y clasificar el código
        code_analysis = self._analyze_code(code, architecture)
        
        # Crear estado inicial del juego
        game_data = {
            "id": game_id,
            "buggy_code": code,
            "architecture": architecture,
            "expected_behavior": expected_behavior,
            "hint": hint,
            "error_description": solution,  # Para evaluación interna
            "code_analysis": code_analysis,
            "answered": False,
            "user_explanation": None,
            "evaluation_result": None,
            "ai_feedback": None,
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
    
    def evaluate_explanation(
        self, 
        game_id: str, 
        user_explanation: str
    ) -> Dict[str, Any]:
        """
        Evalúa la explicación del usuario sobre el error en el código - MEJORADO.
        
        Args:
            game_id: Identificador del juego
            user_explanation: Explicación proporcionada por el usuario
            
        Returns:
            Estado actualizado del juego con evaluación
        """
        game = self._games.get(game_id)
        
        if not game:
            raise ValueError(f"Juego no encontrado: {game_id}")
        
        if game.get("answered", False):
            return game
        
        # Validar que la explicación no esté vacía
        if not user_explanation or len(user_explanation.strip()) < 10:
            raise ValueError("La explicación debe tener al menos 10 caracteres")
        
        # Evaluar la explicación usando análisis de contenido MEJORADO
        evaluation = self._evaluate_user_explanation_enhanced(
            user_explanation, 
            game["error_description"],
            game["buggy_code"],
            game["expected_behavior"]
        )
        
        # Actualizar estado del juego
        game.update({
            "answered": True,
            "user_explanation": user_explanation[:500],  # Limitar longitud
            "evaluation_result": evaluation,
            "updated_at": datetime.now().isoformat()
        })
        
        logger.info(f"Juego de Ensamblador {game_id} evaluado. Puntuación: {evaluation['score']}")
        
        return game
    
    def _evaluate_user_explanation_enhanced(
        self, 
        user_explanation: str, 
        correct_error: str,
        buggy_code: str,
        expected_behavior: str
    ) -> Dict[str, Any]:
        """
        Evalúa la explicación del usuario con criterios mejorados y específicos.
        
        Args:
            user_explanation: Explicación del usuario
            correct_error: Descripción correcta del error
            buggy_code: Código con error
            expected_behavior: Comportamiento esperado
            
        Returns:
            Evaluación detallada mejorada
        """
        # Convertir a minúsculas para comparación
        user_lower = user_explanation.lower()
        error_lower = correct_error.lower()
        
        # Criterios de evaluación mejorados
        evaluation_criteria = {
            "error_identification": 0,  # ¿Identificó el error específico?
            "technical_understanding": 0,  # ¿Demostró comprensión técnica?
            "solution_quality": 0,     # ¿Propuso solución válida?
            "code_analysis": 0         # ¿Analizó el código correctamente?
        }
        
        # 1. Verificar identificación específica del error
        error_keywords = self._extract_technical_keywords(correct_error)
        user_keywords = self._extract_technical_keywords(user_explanation)
        
        matching_keywords = len(error_keywords.intersection(user_keywords))
        if matching_keywords > 0:
            evaluation_criteria["error_identification"] = min(matching_keywords / max(len(error_keywords), 1), 1.0)
        
        # 2. Verificar comprensión técnica específica
        technical_terms = self._get_architecture_terms(buggy_code)
        tech_mentions = sum(1 for term in technical_terms if term in user_lower)
        evaluation_criteria["technical_understanding"] = min(tech_mentions / max(len(technical_terms), 1), 1.0)
        
        # 3. Verificar calidad de la solución propuesta
        solution_indicators = ["debería", "correcto", "cambiar", "usar", "reemplazar", "corregir", "error", "instrucción"]
        solution_mentions = sum(1 for indicator in solution_indicators if indicator in user_lower)
        evaluation_criteria["solution_quality"] = min(solution_mentions / 3, 1.0)
        
        # 4. Verificar análisis específico del código
        code_lines = [line.strip().lower() for line in buggy_code.split('\n') if line.strip()]
        code_analysis = sum(1 for line in code_lines if any(word in user_lower for word in line.split()[:2]))
        evaluation_criteria["code_analysis"] = min(code_analysis / max(len(code_lines), 1), 1.0)
        
        # Calcular puntuación total con pesos específicos
        weights = {
            "error_identification": 0.4,  # 40% - Lo más importante
            "technical_understanding": 0.25,  # 25%
            "solution_quality": 0.25,     # 25%
            "code_analysis": 0.1          # 10%
        }
        
        total_score = sum(evaluation_criteria[key] * weights[key] for key in evaluation_criteria)
        
        # Determinar nivel de corrección con criterios específicos
        if total_score >= 0.85:
            correctness = "excellent"
            feedback = "¡Excelente análisis! Identificaste correctamente el error específico y demostraste comprensión profunda."
        elif total_score >= 0.70:
            correctness = "good"
            feedback = "Buen análisis. Captaste aspectos clave del error, aunque podrías ser más específico en algunos detalles técnicos."
        elif total_score >= 0.50:
            correctness = "partial"
            feedback = "Análisis parcial. Mencionaste algunos puntos relevantes, pero necesitas profundizar en el error específico del código."
        else:
            correctness = "insufficient"
            feedback = "Tu análisis necesita más desarrollo técnico. Revisa línea por línea e identifica qué instrucción específica causa el problema."
        
        return {
            "score": total_score,
            "correctness": correctness,
            "criteria_scores": evaluation_criteria,
            "feedback": feedback[:200],  # Limitar feedback
            "matching_concepts": list(user_keywords.intersection(error_keywords)),
            "technical_depth": len(technical_terms.intersection(set(user_lower.split())))
        }
    
    def _extract_technical_keywords(self, text: str) -> set:
        """
        Extrae palabras clave técnicas específicas de un texto.
        
        Args:
            text: Texto para analizar
            
        Returns:
            Conjunto de palabras clave técnicas
        """
        # Palabras clave técnicas específicas por categoría
        instruction_terms = {
            'add', 'sub', 'mul', 'div', 'mov', 'li', 'lw', 'sw', 'beq', 'bne', 'j', 'jal',
            'push', 'pop', 'call', 'ret', 'inc', 'dec', 'cmp', 'jmp', 'lea'
        }
        
        concept_terms = {
            'register', 'registro', 'instruction', 'instrucción', 'operand', 'operando',
            'stack', 'memoria', 'address', 'dirección', 'immediate', 'inmediato',
            'offset', 'branch', 'jump', 'load', 'store', 'syntax', 'sintaxis'
        }
        
        architecture_terms = {
            'mips', 'x86', 'cpu', 'processor', 'procesador', 'alu', 'pipeline'
        }
        
        all_terms = instruction_terms | concept_terms | architecture_terms
        words = set(text.lower().split())
        return words.intersection(all_terms)
    
    def _get_architecture_terms(self, code: str) -> set:
        """
        Extrae términos de arquitectura específicos del código.
        
        Args:
            code: Código de ensamblador
            
        Returns:
            Conjunto de términos técnicos encontrados
        """
        code_lower = code.lower()
        found_terms = set()
        
        # Detectar arquitectura
        if any(reg in code_lower for reg in ['$t', '$s', '$a', '$v']):
            found_terms.add('mips')
        elif any(reg in code_lower for reg in ['eax', 'ebx', 'ecx', 'edx']):
            found_terms.add('x86')
        
        # Detectar tipos de instrucciones
        if any(instr in code_lower for instr in ['add', 'sub', 'mul', 'div']):
            found_terms.add('arithmetic')
        
        if any(instr in code_lower for instr in ['lw', 'sw', 'mov']):
            found_terms.add('memory')
        
        if any(instr in code_lower for instr in ['beq', 'bne', 'j', 'jmp']):
            found_terms.add('control')
        
        if any(instr in code_lower for instr in ['push', 'pop']):
            found_terms.add('stack')
        
        return found_terms

# AGREGAR MÉTODO PARA RETROALIMENTACIÓN ESPECÍFICA

    def generate_specific_feedback(self, game_id: str) -> Optional[str]:
        """
        Genera feedback educativo específico y técnico para el juego.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Feedback específico o None si el juego no existe
        """
        game = self._games.get(game_id)
        
        if not game or not game.get("answered"):
            return None
        
        evaluation = game.get("evaluation_result", {})
        correctness = evaluation.get("correctness", "insufficient")
        technical_depth = evaluation.get("technical_depth", 0)
        
        # Feedback específico y técnico según el nivel
        feedback_templates = {
            "excellent": [
                f"Excelente dominio técnico. Identificaste correctamente el error específico en '{game.get('architecture', 'código')}'.",
                "Tu análisis demuestra comprensión profunda de la arquitectura y las instrucciones.",
                "Continúa con ejercicios más complejos de optimización y depuración avanzada."
            ],
            "good": [
                f"Buen análisis del código {game.get('architecture', '')}. Captaste el concepto principal.",
                f"Para mejorar: especifica exactamente qué instrucción causa el error y por qué.",
                "Practica identificando errores de sintaxis vs. errores lógicos en ensamblador."
            ],
            "partial": [
                f"Tu análisis toca puntos correctos sobre {game.get('architecture', 'ensamblador')}.",
                f"Necesitas profundizar: el error específico está en '{game.get('hint', 'una instrucción específica')}'.",
                "Revisa la diferencia entre operandos fuente y destino en las instrucciones."
            ],
            "insufficient": [
                f"Revisa los fundamentos de {game.get('architecture', 'ensamblador')} antes de continuar.",
                f"El error en este ejercicio está relacionado con: {game.get('hint', 'la lógica de las instrucciones')}.",
                f"Sugerencia específica: analiza línea por línea qué hace cada instrucción."
            ]
        }
        
        feedback_list = feedback_templates.get(correctness, feedback_templates["insufficient"])
        specific_feedback = " ".join(feedback_list)
        
        # Agregar sugerencia técnica específica si la profundidad técnica es baja
        if technical_depth < 2:
            specific_feedback += f" Tip técnico: estudia las instrucciones {game.get('architecture', 'básicas')} y sus operandos."
        
        return specific_feedback[:300]  # Limitar a 300 caracteres
    
    def _analyze_code(self, code: str, architecture: str) -> Dict[str, Any]:
        """
        Analiza el código para identificar características y posibles errores.
        
        Args:
            code: Código de ensamblador
            architecture: Arquitectura objetivo
            
        Returns:
            Análisis del código
        """
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        
        analysis = {
            "line_count": len(lines),
            "instructions": [],
            "registers_used": set(),
            "instruction_types": set(),
            "complexity": "basic"
        }
        
        for line in lines:
            # Extraer instrucción (primera palabra)
            parts = line.split()
            if parts:
                instruction = parts[0].lower()
                analysis["instructions"].append(instruction)
                analysis["instruction_types"].add(instruction)
                
                # Extraer registros (palabras que empiecen con $ o %)
                for part in parts[1:]:
                    cleaned_part = part.replace(',', '').replace('(', '').replace(')', '')
                    if cleaned_part.startswith('$') or cleaned_part.startswith('%'):
                        analysis["registers_used"].add(cleaned_part)
        
        # Determinar complejidad
        if len(analysis["instruction_types"]) > 4:
            analysis["complexity"] = "advanced"
        elif len(analysis["instruction_types"]) > 2:
            analysis["complexity"] = "intermediate"
        
        return analysis
    
    def _evaluate_user_explanation(
        self, 
        user_explanation: str, 
        correct_error: str,
        buggy_code: str,
        expected_behavior: str
    ) -> Dict[str, Any]:
        """
        Evalúa la explicación del usuario comparándola con el error real.
        
        Args:
            user_explanation: Explicación del usuario
            correct_error: Descripción correcta del error
            buggy_code: Código con error
            expected_behavior: Comportamiento esperado
            
        Returns:
            Evaluación detallada
        """
        # Convertir a minúsculas para comparación
        user_lower = user_explanation.lower()
        error_lower = correct_error.lower()
        
        # Criterios de evaluación
        evaluation_criteria = {
            "error_identification": 0,  # ¿Identificó el error?
            "understanding": 0,         # ¿Demostró comprensión?
            "solution_proposed": 0,     # ¿Propuso solución?
            "technical_accuracy": 0     # ¿Usó terminología correcta?
        }
        
        # 1. Verificar identificación del error
        error_keywords = self._extract_keywords(correct_error)
        user_keywords = self._extract_keywords(user_explanation)
        
        matching_keywords = len(error_keywords.intersection(user_keywords))
        if matching_keywords > 0:
            evaluation_criteria["error_identification"] = min(matching_keywords / len(error_keywords), 1.0)
        
        # 2. Verificar comprensión del concepto
        concept_words = ["registro", "instrucción", "operando", "stack", "memoria", "dirección"]
        concept_mentions = sum(1 for word in concept_words if word in user_lower)
        evaluation_criteria["understanding"] = min(concept_mentions / 3, 1.0)
        
        # 3. Verificar si propuso solución
        solution_indicators = ["debería", "correcto", "cambiar", "usar", "reemplazar", "corregir"]
        solution_mentions = sum(1 for indicator in solution_indicators if indicator in user_lower)
        evaluation_criteria["solution_proposed"] = min(solution_mentions / 2, 1.0)
        
        # 4. Verificar precisión técnica
        # Buscar términos específicos de la arquitectura en la explicación
        architecture_terms = ["mips", "x86", "add", "sub", "mov", "li", "sw", "lw"]
        tech_accuracy = sum(1 for term in architecture_terms if term in user_lower)
        evaluation_criteria["technical_accuracy"] = min(tech_accuracy / 3, 1.0)
        
        # Calcular puntuación total
        total_score = sum(evaluation_criteria.values()) / len(evaluation_criteria)
        
        # Determinar nivel de corrección
        if total_score >= 0.8:
            correctness = "excellent"
            feedback = "¡Excelente análisis! Identificaste correctamente el error y propusiste una solución válida."
        elif total_score >= 0.6:
            correctness = "good"
            feedback = "Buen análisis. Identificaste aspectos clave del error, aunque podrías ser más específico en algunos puntos."
        elif total_score >= 0.4:
            correctness = "partial"
            feedback = "Análisis parcial. Mencionaste algunos aspectos relevantes, pero necesitas profundizar más en el error específico."
        else:
            correctness = "insufficient"
            feedback = "Tu análisis necesita más desarrollo. Revisa el código más cuidadosamente e identifica qué instrucción específica causa el problema."
        
        return {
            "score": total_score,
            "correctness": correctness,
            "criteria_scores": evaluation_criteria,
            "feedback": feedback[:200],  # Limitar feedback
            "matching_concepts": list(user_keywords.intersection(error_keywords))
        }
    
    def _extract_keywords(self, text: str) -> set:
        """
        Extrae palabras clave técnicas de un texto.
        
        Args:
            text: Texto para analizar
            
        Returns:
            Conjunto de palabras clave
        """
        # Palabras clave técnicas relevantes
        technical_terms = {
            'add', 'sub', 'mul', 'div', 'mov', 'li', 'lw', 'sw', 'beq', 'bne', 'j', 'jal',
            'register', 'registro', 'instruction', 'instrucción', 'operand', 'operando',
            'stack', 'memoria', 'address', 'dirección', 'immediate', 'inmediato',
            'offset', 'branch', 'jump', 'load', 'store', 'syntax', 'sintaxis'
        }
        
        words = set(text.lower().split())
        return words.intersection(technical_terms)
    
    def generate_feedback(self, game_id: str) -> Optional[str]:
        """
        Genera feedback educativo personalizado para el juego.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Feedback educativo o None si el juego no existe
        """
        game = self._games.get(game_id)
        
        if not game or not game.get("answered"):
            return None
        
        evaluation = game.get("evaluation_result", {})
        correctness = evaluation.get("correctness", "insufficient")
        
        # Feedback específico según el nivel de corrección
        feedback_templates = {
            "excellent": [
                "Tu análisis demuestra un excelente dominio de los conceptos de ensamblador.",
                "Has identificado correctamente tanto el error como la solución.",
                "Continúa practicando con ejercicios más complejos."
            ],
            "good": [
                "Has mostrado un buen entendimiento del problema.",
                "Para mejorar, trata de ser más específico sobre qué instrucción exacta causa el error.",
                "Practica identificando diferentes tipos de errores en ensamblador."
            ],
            "partial": [
                "Tu análisis toca algunos puntos correctos, pero necesita más profundidad.",
                "Revisa la diferencia entre errores de sintaxis y errores lógicos.",
                "Enfócate en identificar qué instrucción específica no funciona como esperado."
            ],
            "insufficient": [
                "Te recomiendo revisar los conceptos básicos de ensamblador.",
                "Practica identificando errores simples antes de pasar a casos más complejos.",
                f"El error en este caso está relacionado con: {game.get('hint', 'la lógica de las instrucciones')}"
            ]
        }
        
        feedback_list = feedback_templates.get(correctness, feedback_templates["insufficient"])
        return " ".join(feedback_list)[:300]  # Limitar a 300 caracteres
    
    def delete_game(self, game_id: str) -> bool:
        """Elimina un juego del almacenamiento."""
        if game_id in self._games:
            del self._games[game_id]
            logger.info(f"Juego de Ensamblador eliminado: {game_id}")
            return True
        
        return False
    
    def clean_old_games(self, max_age_hours: int = 24) -> int:
        """Elimina juegos antiguos para liberar memoria."""
        import datetime as dt
        
        now = dt.datetime.now()
        cutoff = now - dt.timedelta(hours=max_age_hours)
        cutoff_iso = cutoff.isoformat()
        
        games_to_delete = []
        
        for game_id, game_data in self._games.items():
            created_at = game_data.get("created_at", "")
            if created_at < cutoff_iso:
                games_to_delete.append(game_id)
        
        for game_id in games_to_delete:
            del self._games[game_id]
        
        if games_to_delete:
            logger.info(f"Limpieza: {len(games_to_delete)} juegos de Ensamblador eliminados")
        
        return len(games_to_delete)
# Instancia global del servicio
assembly_service = AssemblyService()