from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn


class EmotionalState(dict):
    """Representa el estado emocional compartido."""


def _state_path() -> Path:
    return Path(__file__).with_name("emotional_state.json")


EMOTIONAL_STATE = EmotionalState()


class EmotionHub:
    """Gestiona y sincroniza el estado emocional del sistema."""

    def __init__(self) -> None:
        self.state = EMOTIONAL_STATE
        self.app = FastAPI(title="Emotion Hub")
        self.clients: Set[WebSocket] = set()
        self._load_state()
        self._setup_routes()

    # ------------------------------------------------------------------
    def _load_state(self) -> None:
        path = _state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if isinstance(data, dict):
                    self.state.update(data)
            except Exception:
                pass

    def _save_state(self) -> None:
        path = _state_path()
        path.write_text(json.dumps(self.state))

    # ------------------------------------------------------------------
    def _setup_routes(self) -> None:
        @self.app.get("/qualia")
        def _get_state():
            return JSONResponse({"state": self.state})

        @self.app.post("/qualia")
        def _set_state(payload: Dict[str, Any]):
            self.state.update(payload)
            self._save_state()
            return JSONResponse({"status": "ok", "state": self.state})

        @self.app.post("/qualia/sync")
        def _sync_state(payload: Dict[str, Any]):
            self.state.clear()
            self.state.update(payload)
            self._save_state()
            return JSONResponse({"status": "ok"})

        @self.app.websocket("/ws/qualia")
        async def _ws(ws: WebSocket):
            await ws.accept()
            self.clients.add(ws)
            await ws.send_json(self.state)
            try:
                while True:
                    data = await ws.receive_json()
                    if isinstance(data, dict):
                        self.state.update(data)
                        self._save_state()
                        for client in list(self.clients):
                            await client.send_json(self.state)
            except WebSocketDisconnect:
                self.clients.remove(ws)

    # ------------------------------------------------------------------
    def run(self, host: str = "127.0.0.1", port: int = 9010) -> None:
        """Arranca el servidor HTTP de EmotionHub."""
        uvicorn.run(self.app, host=host, port=port)
