"""
Servicio para el juego de Diagramas Lógicos.
Gestiona la lógica del juego y el estado de las partidas.
"""

import logging
import json 
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
        self._games: Dict[str, Dict[str, Any]] = {}
        
        # Definición de compuertas lógicas disponibles
        self._gate_types = {
            "AND": lambda inputs: all(inputs),
            "OR": lambda inputs: any(inputs),
            "NOT": lambda inputs: not inputs[0],
            "XOR": lambda inputs: sum(inputs) % 2 == 1,
            "NAND": lambda inputs: not all(inputs),
            "NOR": lambda inputs: not any(inputs),
            "XNOR": lambda inputs: sum(inputs) % 2 == 0
        }
    

    def create_game(
        self, 
        game_id: str, 
        pattern: str,
        question: str,
        input_values: List[List[Union[int, str]]],
        expected_output: List[Union[int, str]]
    ) -> Dict[str, Any]:
        """
        Crea un nuevo juego de Diagrama Lógico con debugging mejorado.
        """
        try:
            # DEBUG: Log de la información recibida
            logger.info(f"Creando juego de lógica {game_id}")
            logger.info(f"Pattern recibido: {pattern}")
            logger.info(f"Question: {question}")
            logger.info(f"Input values: {input_values}")
            logger.info(f"Expected output: {expected_output}")
            
            # Parsear la estructura del circuito
            if isinstance(pattern, str):
                try:
                    circuit_data = json.loads(pattern)
                    logger.info(f"Pattern parseado exitosamente: {circuit_data}")
                except json.JSONDecodeError as json_error:
                    logger.error(f"Error parseando JSON: {json_error}")
                    logger.error(f"Pattern string: {pattern}")
                    raise ValueError(f"Error parseando JSON del pattern: {json_error}")
            else:
                circuit_data = pattern
                logger.info(f"Pattern ya es dict: {circuit_data}")
            
            # Verificar estructura
            logger.info(f"Claves disponibles en circuit_data: {list(circuit_data.keys())}")
            
            # Validar estructura simplificada
            if "pattern" not in circuit_data:
                if "gates_sequence" in circuit_data:
                    logger.info("Convirtiendo gates_sequence a pattern para compatibilidad")
                    circuit_data["pattern"] = circuit_data["gates_sequence"]
                else:
                    logger.error("No se encontró 'pattern' ni 'gates_sequence' en la estructura")
                    logger.error(f"Estructura recibida: {circuit_data}")
                    
                    # Crear estructura de emergencia
                    circuit_data["pattern"] = ["AND"]  # Fallback mínimo
                    circuit_data["input_values"] = [[1, 0, 0]]
                    circuit_data["expected_output"] = 0
                    circuit_data["complexity_type"] = "single_output"
                    logger.info("Creada estructura de emergencia")
            
            # Obtener el primer valor de salida esperada para compatibilidad
            final_expected_output = expected_output[0] if isinstance(expected_output, list) else expected_output
            
            # Crear estado inicial del juego
            game_data = {
                "id": game_id,
                "circuit_structure": circuit_data,
                "question": question,
                "pattern_list": circuit_data.get("pattern", []),
                "input_matrix": circuit_data.get("input_values", []),
                "expected_output": final_expected_output,
                "complexity_type": circuit_data.get("complexity_type", "single_output"),
                "difficulty": circuit_data.get("difficulty", "easy"),
                "test_cases": circuit_data.get("test_cases", []),
                "answered": False,
                "user_answer": None,
                "correct": None,
                "created_at": datetime.now().isoformat()
            }
            
            # Guardar juego
            self._games[game_id] = game_data
            logger.info(f"Juego de Diagrama Lógico creado exitosamente: {game_id}")
            logger.info(f"Complejidad: {circuit_data.get('complexity_type', 'single_output')}")
            
            return game_data
            
        except Exception as e:
            logger.error(f"Error completo al crear juego de lógica {game_id}: {str(e)}")
            logger.error(f"Tipo de error: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Error en la estructura del circuito: {str(e)}")
    
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
    
    def evaluate_circuit(
        self, 
        game_id: str, 
        user_answer: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Evalúa la respuesta del usuario para el circuito lógico - CORREGIDO.
        
        Args:
            game_id: Identificador del juego
            user_answer: Respuesta única del usuario (0 o 1)
            
        Returns:
            Estado actualizado del juego con resultado de evaluación
        """
        game = self._games.get(game_id)
        
        if not game:
            raise ValueError(f"Juego no encontrado: {game_id}")
        
        if game.get("answered", False):
            return game
        
        # Normalizar respuesta del usuario
        try:
            user_output = int(user_answer)
            if user_output not in [0, 1]:
                raise ValueError("La respuesta debe ser 0 o 1")
        except (ValueError, TypeError):
            raise ValueError("Respuesta inválida. Use 0 o 1.")
        
        # Obtener salida esperada
        expected_output = game.get("expected_output", 0)
        
        # Para compatibilidad, convertir a int si es posible
        if isinstance(expected_output, (list, dict)):
            # Si es lista, tomar el primer elemento
            if isinstance(expected_output, list) and len(expected_output) > 0:
                expected_output = expected_output[0]
            # Si es dict y es de casos múltiples, convertir a evaluación simple para este método
            elif isinstance(expected_output, dict):
                # Para casos múltiples, este método no es apropiado, usar evaluate_complex_circuit
                raise ValueError("Use evaluate_complex_circuit para respuestas complejas")
        
        expected_output = int(expected_output)
        
        # Evaluar si es correcta
        is_correct = user_output == expected_output
        
        # Verificar la evaluación simulando el circuito (opcional, para validación)
        circuit_structure = game.get("circuit_structure", {})
        test_input = game.get("input_matrix", [])
        
        if test_input:
            # Usar la primera fila como entrada para simulación
            first_row = test_input[0] if test_input else []
            circuit_evaluation = self._simulate_circuit(circuit_structure, first_row[:-1] if first_row else [])
        else:
            circuit_evaluation = {"valid": True, "message": "Sin datos para simulación"}
        
        # Actualizar estado del juego
        game.update({
            "answered": True,
            "user_answer": user_output,
            "correct": is_correct,
            "circuit_simulation": circuit_evaluation,
            "updated_at": datetime.now().isoformat()
        })
        
        logger.info(f"Juego de Diagrama Lógico {game_id} evaluado. Correcto: {is_correct}")
        
        return game


    def get_circuit_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada del circuito para explicaciones.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Información del circuito o None si no existe
        """
        game = self._games.get(game_id)
        
        if not game:
            return None
        
        circuit_structure = game["circuit_structure"]
        
        return {
            "description": circuit_structure.get("description", ""),
            "gates_sequence": circuit_structure.get("gates_sequence", []),
            "connections": circuit_structure.get("gate_connections", {}),
            "inputs_count": circuit_structure.get("inputs_count", 2),
            "test_case": {
                "inputs": game["test_input"],
                "expected_output": game["expected_output"]
            },
            "user_answer": game.get("user_answer"),
            "correct": game.get("correct")
        }

    def _simulate_circuit(self, circuit_structure: Dict, inputs: List[int]) -> Dict[str, Any]:
        """
        Simula la ejecución del circuito lógico para validación - ACTUALIZADO.
        
        Args:
            circuit_structure: Estructura del circuito con compuertas y conexiones
            inputs: Valores de entrada del circuito
            
        Returns:
            Resultado de la simulación paso a paso
        """
        try:
            # Usar "pattern" en lugar de "gates_sequence"
            pattern = circuit_structure.get("pattern", [])
            input_values = circuit_structure.get("input_values", [])
            
            # Si no hay input_values, crear simulación básica
            if not input_values:
                return {
                    "valid": True,
                    "steps": [],
                    "final_output": 0,
                    "message": "Simulación básica - sin datos de entrada detallados"
                }
            
            # Estado de las señales en el circuito
            signals = {}
            
            # Inicializar entradas
            for i, value in enumerate(inputs):
                signals[f"IN{i+1}"] = int(value)
            
            # Procesar compuertas en secuencia usando la nueva estructura
            simulation_steps = []
            
            for i, (gate_type, values) in enumerate(zip(pattern, input_values)):
                # Extraer entradas y salida de la matriz
                gate_inputs = values[:-1]  # Todos excepto el último
                gate_output_value = values[-1]  # El último es la salida
                
                # Calcular salida esperada de la compuerta
                if gate_type in self._gate_types:
                    gate_function = self._gate_types[gate_type]
                    calculated_output = int(gate_function(gate_inputs))
                    
                    # Verificar si la salida calculada coincide con la esperada
                    is_valid = calculated_output == gate_output_value
                    
                    simulation_steps.append({
                        "step": i + 1,
                        "gate": gate_type,
                        "inputs": gate_inputs,
                        "expected_output": gate_output_value,
                        "calculated_output": calculated_output,
                        "valid": is_valid
                    })
                    
                    # Actualizar señales para la siguiente compuerta
                    signals[f"G{i+1}_OUT"] = gate_output_value
                    
                else:
                    simulation_steps.append({
                        "step": i + 1,
                        "gate": gate_type,
                        "error": f"Tipo de compuerta desconocido: {gate_type}"
                    })
            
            # La salida final es la salida de la última compuerta
            final_output = input_values[-1][-1] if input_values else 0
            
            # Verificar si todo el circuito es válido
            all_valid = all(step.get("valid", False) for step in simulation_steps if "error" not in step)
            
            return {
                "valid": all_valid,
                "steps": simulation_steps,
                "final_output": final_output,
                "all_signals": signals
            }
            
        except Exception as e:
            logger.error(f"Error simulando circuito: {str(e)}")
            return {
                "valid": False,
                "error": str(e), 
                "final_output": 0,
                "message": "Error en la simulación del circuito"
            }

    def add_detailed_explanation(self, game_id: str, explanation: str) -> bool:
        """
        Agrega una explicación detallada a un juego respondido.
        
        Args:
            game_id: Identificador del juego
            explanation: Explicación detallada del funcionamiento del circuito
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        game = self._games.get(game_id)
        
        if not game or not game.get("answered"):
            return False
        
        # Limitar explicación a 400 caracteres para mantener respuestas concisas
        game["detailed_explanation"] = explanation[:400]
        return True

    def get_circuit_visualization(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Genera información para visualizar el circuito - ACTUALIZADO.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Estructura de datos para visualización del circuito
        """
        game = self._games.get(game_id)
        
        if not game:
            return None
        
        circuit_structure = game["circuit_structure"]
        
        return {
            "description": circuit_structure.get("description", ""),
            "pattern": circuit_structure.get("pattern", []),  # Usar "pattern" en lugar de "gates_sequence"
            "connections": circuit_structure.get("gate_connections", {}),
            "inputs_count": circuit_structure.get("inputs_count", 2),
            "complexity_type": circuit_structure.get("complexity_type", "single_output"),
            "test_case": {
                "inputs": game.get("input_matrix", []),
                "expected_output": game.get("expected_output", 0)
            },
            "user_answer": game.get("user_answer"),
            "correct": game.get("correct")
        }
    
    def delete_game(self, game_id: str) -> bool:
        """Elimina un juego del almacenamiento."""
        if game_id in self._games:
            del self._games[game_id]
            logger.info(f"Juego de Diagrama Lógico eliminado: {game_id}")
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
            logger.info(f"Limpieza: {len(games_to_delete)} juegos de Diagrama Lógico eliminados")
        
        return len(games_to_delete)

    def evaluate_complex_circuit(
        self, 
        game_id: str, 
        user_answer: Union[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evalúa la respuesta del usuario para circuitos con complejidad variable.
        
        Args:
            game_id: Identificador del juego
            user_answer: Respuesta del usuario (varía según complejidad)
            
        Returns:
            Estado actualizado del juego con resultado de evaluación
        """
        game = self._games.get(game_id)
        
        if not game:
            raise ValueError(f"Juego no encontrado: {game_id}")
        
        if game.get("answered", False):
            return game
        
        # Obtener datos del circuito
        circuit_structure = game["circuit_structure"]
        complexity_type = circuit_structure.get("complexity_type", "single_output")
        expected_output = circuit_structure.get("expected_output", 0)
        
        # Evaluar según complejidad
        if complexity_type == "single_output":
            evaluation_result = self._evaluate_simple_circuit_answer(user_answer, expected_output)
        elif complexity_type == "multiple_cases":
            evaluation_result = self._evaluate_multiple_cases_circuit_answer(user_answer, expected_output)
        elif complexity_type == "pattern_analysis":
            evaluation_result = self._evaluate_pattern_analysis_circuit_answer(user_answer, expected_output)
        else:
            evaluation_result = {"correct": False, "error": "Tipo de complejidad desconocido"}
        
        # Actualizar estado del juego
        game.update({
            "answered": True,
            "user_answer": user_answer,
            "correct": evaluation_result.get("correct", False),
            "evaluation_result": evaluation_result,
            "updated_at": datetime.now().isoformat()
        })
        
        logger.info(f"Juego de Diagrama Lógico {game_id} evaluado. Correcto: {evaluation_result.get('correct', False)}")
        
        return game

    def _evaluate_simple_circuit_answer(
        self, 
        user_answer: Union[int, str], 
        expected_output: Union[int, str]
    ) -> Dict[str, Any]:
        """Evalúa respuesta simple (easy)."""
        try:
            user_val = int(user_answer)
            expected_val = int(expected_output)
            
            if user_val not in [0, 1]:
                return {"correct": False, "error": "La respuesta debe ser 0 o 1"}
            
            correct = user_val == expected_val
            return {
                "correct": correct,
                "score": 1.0 if correct else 0.0,
                "feedback": "Correcto" if correct else f"Incorrecto, la respuesta era {expected_val}"
            }
        except (ValueError, TypeError):
            return {"correct": False, "error": "Respuesta inválida"}
    
    def _evaluate_multiple_cases_circuit_answer(
        self, 
        user_answer: Dict[str, Any], 
        expected_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evalúa respuesta de múltiples casos (medium)."""
        if not isinstance(user_answer, dict):
            return {"correct": False, "error": "Se esperaba un diccionario con casos"}
        
        if not isinstance(expected_output, dict):
            return {"correct": False, "error": "Configuración de salida esperada inválida"}
        
        total_cases = len(expected_output)
        correct_cases = 0
        case_results = {}
        
        for case_id, expected_val in expected_output.items():
            user_val = user_answer.get(case_id)
            
            if user_val is None:
                case_results[case_id] = "missing"
            else:
                try:
                    user_val_int = int(user_val)
                    expected_val_int = int(expected_val)
                    
                    if user_val_int == expected_val_int:
                        correct_cases += 1
                        case_results[case_id] = "correct"
                    else:
                        case_results[case_id] = f"incorrect (expected {expected_val_int}, got {user_val_int})"
                except (ValueError, TypeError):
                    case_results[case_id] = "invalid format"
        
        partial_score = correct_cases / total_cases if total_cases > 0 else 0.0
        all_correct = correct_cases == total_cases
        
        return {
            "correct": all_correct,
            "partial_score": partial_score,
            "case_results": case_results,
            "feedback": f"Casos correctos: {correct_cases}/{total_cases}",
            "score": partial_score
        }
    
    def _evaluate_pattern_analysis_circuit_answer(
        self, 
        user_answer: Dict[str, Any], 
        expected_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evalúa respuesta de análisis de patrones (hard)."""
        if not isinstance(user_answer, dict):
            return {"correct": False, "error": "Se esperaba un diccionario con análisis de patrón"}
        
        if not isinstance(expected_output, dict):
            return {"correct": False, "error": "Configuración de patrón esperado inválida"}
        
        total_components = len(expected_output)
        correct_components = 0
        component_results = {}
        
        for component, expected_val in expected_output.items():
            user_val = user_answer.get(component)
            
            if component == "pattern":
                # Evaluar patrón de secuencia
                if isinstance(user_val, list) and isinstance(expected_val, list):
                    if len(user_val) == len(expected_val):
                        matches = sum(1 for u, e in zip(user_val, expected_val) if u == e)
                        pattern_accuracy = matches / len(expected_val)
                        
                        if pattern_accuracy >= 0.8:  # 80% de precisión mínima
                            correct_components += 1
                            component_results[component] = f"correct ({pattern_accuracy:.1%})"
                        else:
                            component_results[component] = f"partial ({pattern_accuracy:.1%})"
                    else:
                        component_results[component] = f"wrong length (expected {len(expected_val)}, got {len(user_val) if user_val else 0})"
                else:
                    component_results[component] = "invalid format (expected list)"
            
            else:
                # Evaluar componentes individuales (cycle_length, final_state, etc.)
                if user_val == expected_val:
                    correct_components += 1
                    component_results[component] = "correct"
                else:
                    component_results[component] = f"incorrect (expected {expected_val}, got {user_val})"
        
        partial_score = correct_components / total_components if total_components > 0 else 0.0
        all_correct = correct_components == total_components
        
        return {
            "correct": all_correct,
            "partial_score": partial_score,
            "component_results": component_results,
            "feedback": f"Componentes correctos: {correct_components}/{total_components}",
            "score": partial_score
        }
    
    def get_complexity_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información sobre la complejidad del juego.
        
        Args:
            game_id: Identificador del juego
            
        Returns:
            Información de complejidad del juego
        """
        game = self._games.get(game_id)
        
        if not game:
            return None
        
        circuit_structure = game["circuit_structure"]
        
        return {
            "complexity_type": circuit_structure.get("complexity_type", "single_output"),
            "pattern": circuit_structure.get("pattern", []),
            "expected_output": circuit_structure.get("expected_output"),
            "difficulty": circuit_structure.get("difficulty", "easy"),
            "test_cases": circuit_structure.get("test_cases", []),
            "user_answer": game.get("user_answer"),
            "evaluation_result": game.get("evaluation_result", {}),
            "answered": game.get("answered", False)
        }

# Instancia global del servicio
logic_diagram_service = LogicDiagramService()