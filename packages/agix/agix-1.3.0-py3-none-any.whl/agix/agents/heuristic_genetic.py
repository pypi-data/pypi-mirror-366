"""Agente genético con heurísticas evolutivas."""

from __future__ import annotations

import numpy as np

from typing import Optional

from src.agix.agents.genetic import GeneticAgent
from src.agix.learning.heuristic_evolution import HeuristicEvolution
from src.agix.learning.continual_trainer import ContinuousHeuristicTrainer
from src.agix.qualia.spirit import QualiaSpirit


class HeuristicGeneticAgent(GeneticAgent):
    """Extensión de :class:`GeneticAgent` que usa heurísticas de memoria."""

    def __init__(
        self,
        action_space_size,
        chromosome_length=10,
        mutation_rate=0.1,
        qualia: Optional[QualiaSpirit] = None,
    ):
        super().__init__(
            action_space_size,
            chromosome_length,
            mutation_rate,
            qualia=qualia,
        )
        self.heuristic = HeuristicEvolution(chromosome_length)

    # ------------------------------------------------------------------
    def reset(self, trainer: ContinuousHeuristicTrainer | None = None):
        super().reset()
        if trainer is not None:
            trainer.end_episode(self)
        else:
            self.chromosome = self.heuristic.generar_parametros(self.memory)

    # ------------------------------------------------------------------
    def evolve_from_population(self, population: list[GeneticAgent], fitness: list[float]):
        """Actualiza el cromosoma usando la población evaluada."""
        cromosomas = [agent.chromosome for agent in population]
        mejores = self.heuristic.seleccionar_mejores(cromosomas, fitness)
        if mejores:
            self.chromosome = np.mean(mejores, axis=0)
