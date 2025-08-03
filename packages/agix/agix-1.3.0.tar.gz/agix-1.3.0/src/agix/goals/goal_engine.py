# goal_engine.py

from typing import List, Optional
import uuid
import datetime


class Goal:
    """
    Representa una meta individual con descripción, prioridad, estado y timestamp.
    """

    def __init__(self, descripcion: str, prioridad: int = 5):
        self.id = str(uuid.uuid4())
        self.descripcion = descripcion
        self.prioridad = prioridad  # 1 (alta) - 10 (baja)
        self.estado = "pendiente"   # otros: "en_progreso", "cumplida", "fallida"
        self.timestamp_creacion = datetime.datetime.now()
        self.timestamp_finalizacion = None

    def marcar_cumplida(self):
        self.estado = "cumplida"
        self.timestamp_finalizacion = datetime.datetime.now()

    def marcar_fallida(self):
        self.estado = "fallida"
        self.timestamp_finalizacion = datetime.datetime.now()

    def __repr__(self):
        return f"<Goal {self.descripcion} ({self.estado})>"


class GoalEngine:
    """
    Gestiona el conjunto de metas del agente.
    Puede añadir, actualizar, priorizar y evaluar metas.
    """

    def __init__(self):
        self.metas: List[Goal] = []

    def agregar_meta(self, descripcion: str, prioridad: int = 5) -> Goal:
        nueva = Goal(descripcion, prioridad)
        self.metas.append(nueva)
        self.ordenar_por_prioridad()
        return nueva

    def metas_activas(self) -> List[Goal]:
        return [m for m in self.metas if m.estado in ["pendiente", "en_progreso"]]

    def metas_cumplidas(self) -> List[Goal]:
        return [m for m in self.metas if m.estado == "cumplida"]

    def ordenar_por_prioridad(self):
        self.metas.sort(key=lambda m: m.prioridad)

    def buscar_meta(self, id_meta: str) -> Optional[Goal]:
        return next((m for m in self.metas if m.id == id_meta), None)

    def resumen_metas(self) -> str:
        return f"Total metas: {len(self.metas)} | Activas: {len(self.metas_activas())} | Cumplidas: {len(self.metas_cumplidas())}"
