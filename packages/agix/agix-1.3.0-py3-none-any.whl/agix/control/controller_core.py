# controller_core.py

from typing import Any, Dict, List

import logging

from src.agix.control.policy_optimization import PolicyOptimizer
from src.agix.control.strategy_evaluator import StrategyPerformanceTracker

logger = logging.getLogger(__name__)


class ControllerCore:
    """
    Núcleo del sistema de control jerárquico.
    Se encarga de seleccionar políticas activas, gestionar su ciclo y evaluar rendimiento.
    """

    def __init__(self, policy_optimizer: PolicyOptimizer,
                 performance_threshold: float = 0.3,
                 performance_cycles: int = 3):
        self.policy_optimizer = policy_optimizer
        # Seguimiento de rendimiento de estrategias
        self.performance_tracker = StrategyPerformanceTracker()
        self.performance_threshold = performance_threshold
        self.performance_cycles = performance_cycles
        self.estado_interno = {}
        self.historial_politicas = []
        self.politica_actual = None
        # Historial de rendimiento por estrategia
        self.historial_estrategias: Dict[str, List[float]] = {}
        # Pesos asignados a cada estrategia para priorizar su selección
        self.pesos_estrategia: Dict[str, float] = {}

    def disable_strategy(self, name: str) -> None:
        """Elimina la estrategia indicada de los pesos."""
        if name in self.pesos_estrategia:
            del self.pesos_estrategia[name]

    def seleccionar_politica(self, contexto: Any) -> Any:
        """
        Selecciona una política en base al contexto (percepción, metas, estado emocional).
        Por ahora retorna una política dummy, puede integrarse con módulos externos.
        """
        if not self.pesos_estrategia:
            # Valor por defecto para garantizar que exista al menos una estrategia
            self.pesos_estrategia["default_policy"] = 1.0

        # Seleccionar la estrategia con mayor peso asignado
        self.politica_actual = max(self.pesos_estrategia, key=self.pesos_estrategia.get)
        self.historial_politicas.append(self.politica_actual)
        self.historial_estrategias.setdefault(self.politica_actual, [])
        return self.politica_actual

    def evaluar_desempeno(self, resultados: Any) -> float:
        """
        Evalúa el rendimiento reciente para decidir si adaptar la política.
        """
        # Dummy: puedes usar recompensas promedio, feedback emocional o métricas éticas
        return resultados.get("reward", 0.0)

    def ciclo_control(self, percepcion: Any, metas: Any, retroalimentacion: Any):
        """
        Bucle principal del controlador:
        1. Selecciona política según contexto.
        2. Evalúa desempeño.
        3. Decide si invocar optimización de política.
        """
        self.seleccionar_politica(percepcion)
        score = self.evaluar_desempeno(retroalimentacion)
        # Registrar el desempeño obtenido
        self.historial_estrategias.setdefault(self.politica_actual, []).append(score)
        self.performance_tracker.register_result(self.politica_actual, score)
        # Utilizar el resumen para actualizar los pesos
        self.actualizar_pesos()

        if self.performance_tracker.low_performance(
            self.politica_actual,
            threshold=self.performance_threshold,
            min_samples=self.performance_cycles,
        ):
            logger.info(
                "⚠️ Estrategia con rendimiento bajo. Se deshabilita la estrategia."
            )
            estrategia_anterior = self.politica_actual
            self.disable_strategy(estrategia_anterior)
            self.seleccionar_politica(percepcion)
            logger.info(
                "AGIX cambió de estrategia '%s' por bajo rendimiento en %d casos similares",
                self.politica_actual,
                self.performance_cycles,
            )

        if score < 0.5:  # umbral adaptable
            logger.info("🔄 Ajustando política...")
            try:
                self.policy_optimizer.update_policy(
                    states=retroalimentacion["states"],
                    actions=retroalimentacion["actions"],
                    advantages=retroalimentacion["advantages"]
                )
            except NotImplementedError:
                logger.warning("⚠️ Método update_policy aún no implementado.")

    def resumen_estado(self) -> str:
        return f"Política actual: {self.politica_actual} | Historial: {self.historial_politicas[-3:]}"

    def obtener_rendimiento_estrategia(self, nombre: str) -> Dict[str, float]:
        """Calcula estadísticos de rendimiento para una estrategia."""
        return self.performance_tracker.summary(nombre)

    def actualizar_pesos(self) -> None:
        """Actualiza los pesos de las estrategias según su rendimiento histórico."""
        estrategias = set(self.historial_estrategias.keys()) | set(self.performance_tracker.history.keys())
        for estrategia in estrategias:
            datos = self.performance_tracker.summary(estrategia)
            promedio = datos["promedio"]
            if promedio == 0.0 and self.historial_estrategias.get(estrategia):
                historial = self.historial_estrategias[estrategia]
                promedio = sum(historial) / len(historial)
            peso_actual = self.pesos_estrategia.get(estrategia, 1.0)
            if promedio >= 0.5:
                self.pesos_estrategia[estrategia] = peso_actual + 0.1
            else:
                self.pesos_estrategia[estrategia] = max(0.0, peso_actual - 0.1)
