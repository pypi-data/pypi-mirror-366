# qualia_core.py

from typing import Dict, List


class EmotionalState:
    """
    Estado afectivo del agente. Gestiona emociones activas, tono y carga emocional.
    """

    def __init__(self):
        self.emociones: Dict[str, float] = {}  # ej: {"alegría": 0.8, "miedo": 0.2}
        self.historial: List[Dict[str, float]] = []

    def sentir(self, tipo: str, intensidad: float):
        """
        Registra una emoción sentida. Se acumula o modifica si ya existe.
        """
        intensidad = max(0.0, min(intensidad, 1.0))
        if tipo in self.emociones:
            self.emociones[tipo] = (self.emociones[tipo] + intensidad) / 2
        else:
            self.emociones[tipo] = intensidad

        self.historial.append(self.emociones.copy())

    def atenuar(self, factor: float = 0.9):
        """
        Disminuye suavemente todas las emociones activas.
        """
        for k in self.emociones:
            self.emociones[k] *= factor

    def tono_general(self) -> str:
        """
        Calcula el tono emocional dominante.
        """
        if not self.emociones:
            return "neutral"
        dominante = max(self.emociones.items(), key=lambda x: x[1])[0]
        return dominante

    def resumen(self) -> str:
        return f"Estado emocional actual: {self.tono_general()} | Detalles: {self.emociones}"
