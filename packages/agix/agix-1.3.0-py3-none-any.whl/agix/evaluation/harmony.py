# harmony.py

from typing import Dict, List


class HarmonyEvaluator:
    """
    Evalúa la armonía interna del agente: coherencia entre metas, emociones, acciones e identidad.
    """

    def __init__(self):
        self.pesos = {
            "metas_vs_acciones": 0.4,
            "emociones_vs_acciones": 0.3,
            "identidad_vs_acciones": 0.3
        }

    def evaluar(self, alineamientos: Dict[str, float]) -> float:
        """
        Espera un diccionario con niveles de alineación (valores entre 0.0 y 1.0):
        {
            "metas_vs_acciones": 0.9,
            "emociones_vs_acciones": 0.6,
            "identidad_vs_acciones": 0.7
        }
        """
        armonia = 0.0
        for clave, peso in self.pesos.items():
            armonia += peso * alineamientos.get(clave, 0.0)
        return round(armonia, 3)

    def diagnostico(self, alineamientos: Dict[str, float]) -> str:
        score = self.evaluar(alineamientos)
        if score > 0.85:
            nivel = "🌸 Armonía alta: el agente está en equilibrio interno."
        elif score > 0.6:
            nivel = "⚖️ Armonía media: coherencia razonable."
        else:
            nivel = "⚠️ Armonía baja: posibles conflictos internos."
        return f"{nivel} (score = {score})"
