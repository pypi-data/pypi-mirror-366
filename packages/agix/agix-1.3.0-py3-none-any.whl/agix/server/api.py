from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Tuple
from threading import Lock

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.agix.adapters.service import ServiceAdapter

from src.agix.architecture.ameta import AMetaArchitecture, AGIModule
from src.agix.memory import GestorDeMemoria


class PerceptionModule(AGIModule):
    """Módulo de percepción que pasa la observación sin cambios."""

    def process(self, observation: Any) -> Any:
        return observation


class InferenceModule(AGIModule):
    """Módulo de inferencia mínimo."""

    def process(self, data: Any) -> Any:
        return data


class DecisionModule(AGIModule):
    """Calcula una acción numérica simple a partir de la observación."""

    def process(self, inferred_state: Any) -> int:
        if isinstance(inferred_state, (list, tuple)):
            return len(inferred_state)
        if isinstance(inferred_state, (int, float)):
            return int(inferred_state)
        return 0


class MemoryModule(AGIModule):
    """Registra experiencias en ``GestorDeMemoria``."""

    def __init__(self, memory: GestorDeMemoria) -> None:
        self.memory = memory

    def process(self, experience: Tuple[Any, Any]) -> None:
        obs, action = experience
        # Sincronizamos el registro para evitar condiciones de carrera
        # en entornos multi-hilo.
        with memory_lock:
            self.memory.registrar(str(obs), str(action), "", True)


memory_manager = GestorDeMemoria()
# Lock para sincronizar accesos concurrentes a la memoria y evitar
# corrupci\u00f3n de datos.
memory_lock = Lock()
architecture = AMetaArchitecture(
    P=PerceptionModule(),
    I=InferenceModule(),
    D=DecisionModule(),
    M=MemoryModule(memory_manager),
)

service_adapter = ServiceAdapter()

app = FastAPI(title="AGIX API")


@app.post("/infer")
def infer(payload: Dict[str, Any]):
    """Procesa una observación y devuelve la acción calculada."""
    observation = service_adapter.adapt_input(payload)
    action = architecture.cycle(observation)
    return JSONResponse(service_adapter.adapt_output(action))


@app.post("/learn")
def learn(payload: Dict[str, Any]):
    """Guarda una experiencia completa proporcionada por el usuario."""
    with memory_lock:
        architecture.modules["M"].memory.registrar(
            str(payload.get("entrada", "")),
            str(payload.get("decision", "")),
            str(payload.get("resultado", "")),
            bool(payload.get("exito", True)),
        )
    return JSONResponse({"status": "ok"})


@app.get("/memory")
def get_memory():
    """Devuelve las experiencias almacenadas."""
    with memory_lock:
        data = [asdict(exp) for exp in memory_manager.experiencias]
    return JSONResponse({"experiencias": data})
