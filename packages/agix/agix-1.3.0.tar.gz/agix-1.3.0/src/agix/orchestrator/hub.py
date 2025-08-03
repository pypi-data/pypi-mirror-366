from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn


class QualiaHub:
    """Orquestador central de módulos AGIX."""

    def __init__(self) -> None:
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.app = FastAPI(title="Qualia Hub")
        self._setup_routes()

    # ------------------------------------------------------------------
    def _setup_routes(self) -> None:
        @self.app.post("/register")
        def _register(payload: Dict[str, Any]):
            name = str(payload.get("name"))
            metadata = payload.get("metadata", {})
            if name:
                self.register_module(name, metadata)
            return JSONResponse({"status": "ok"})

        @self.app.get("/modules")
        def _modules():
            return JSONResponse({"modules": self.modules})

        @self.app.post("/event")
        def _event(payload: Dict[str, Any]):
            event = payload.get("event", "")
            self.broadcast_event(event)
            return JSONResponse({"status": "ok"})

    # ------------------------------------------------------------------
    def register_module(self, name: str, metadata: Dict[str, Any]) -> None:
        """Registra un módulo junto a sus metadatos."""
        self.modules[name] = metadata

    def get_modules(self) -> Dict[str, Dict[str, Any]]:
        """Devuelve la tabla de módulos registrados."""
        return self.modules

    def broadcast_event(self, event: str) -> None:
        """Difunde un evento a los módulos registrados (solo log)."""
        print(f"Evento difundido: {event}")

    def run(self, host: str = "127.0.0.1", port: int = 9000, emotion: bool = False) -> None:
        """Arranca el servidor HTTP de QualiaHub o del EmotionHub."""
        if emotion:
            from .emotion_hub import EmotionHub

            EmotionHub().run(host=host, port=port)
            return
        uvicorn.run(self.app, host=host, port=port)
