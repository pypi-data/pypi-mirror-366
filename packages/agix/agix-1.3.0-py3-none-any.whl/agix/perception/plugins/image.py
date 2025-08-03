
import numpy as np

from src.agix.perception.plugins import SensorPlugin


class ImagePlugin(SensorPlugin):
    """Convierte listas de píxeles en arrays NumPy."""

    def process(self, raw_input):
        return np.asarray(raw_input)
