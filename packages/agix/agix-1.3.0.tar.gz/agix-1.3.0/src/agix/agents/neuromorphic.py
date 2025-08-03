# agi_lab/agents/neuromorphic.py

import numpy as np
from typing import Optional

from src.agix.agents.base import AGIAgent
from src.agix.qualia.spirit import QualiaSpirit


class PlasticSynapse:
    """
    Modelo simple de sinapsis plástica usando una regla hebbiana modificada.
    """
    def __init__(self, input_size, output_size, learning_rate=0.01):
        self.weights = np.random.uniform(-0.5, 0.5, (output_size, input_size))
        self.learning_rate = learning_rate

    def forward(self, x):
        return np.dot(self.weights, x)

    def hebbian_update(self, x, y):
        """
        Regla hebbiana: Δw_ij = η * y_i * x_j
        """
        delta_w = self.learning_rate * np.outer(y, x)
        self.weights += delta_w


class NeuromorphicAgent(AGIAgent):
    """
    Agente con arquitectura inspirada en redes neuronales plásticas.
    """
    def __init__(
        self,
        input_size,
        output_size,
        learning_rate=0.01,
        qualia: Optional[QualiaSpirit] = None,
    ):
        super().__init__(name="NeuromorphicAgent", qualia=qualia)
        self.input_size = input_size
        self.output_size = output_size
        self.synapse = PlasticSynapse(input_size, output_size, learning_rate)
        self.last_input = None
        self.last_output = None

    def perceive(self, observation):
        x = np.asarray(observation).flatten()
        x = x[:self.input_size]  # Truncar si necesario
        self.last_input = x
        self.last_output = self.synapse.forward(x)

    def decide(self):
        if self.last_output is None:
            return np.random.randint(self.output_size)
        action = int(np.argmax(self.last_output))
        return action

    def learn(self, reward, done=False):
        if self.last_input is None or self.last_output is None:
            return
        y = self.last_output * reward  # Modulación por refuerzo
        self.synapse.hebbian_update(self.last_input, y)

    def reset(self):
        super().reset()
        self.synapse = PlasticSynapse(self.input_size, self.output_size)
