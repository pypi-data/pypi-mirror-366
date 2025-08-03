from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

try:
    import websockets
except Exception:  # pragma: no cover - optional dependency
    websockets = None


class QualiaNetworkClient:
    """Cliente sencillo para sincronizar estados emocionales por red."""

    def __init__(self, base_url: str, session: Optional[Any] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    # ----------------------------- HTTP ---------------------------------
    def enviar_estado(self, estado: Dict[str, Any]) -> Any:
        """Env\u00eda el estado emocional por HTTP POST."""
        url = f"{self.base_url}/qualia/sync"
        return self.session.post(url, json=estado)

    def obtener_estado(self) -> Dict[str, Any]:
        """Recupera el estado emocional remoto por HTTP."""
        url = f"{self.base_url}/qualia"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    # ---------------------------- WebSocket ------------------------------
    async def enviar_estado_ws(self, estado: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Env\u00eda el estado emocional usando WebSocket si est\u00e1 disponible."""
        if websockets is None:
            raise RuntimeError("websockets no instalado")
        async with websockets.connect(f"{self.base_url}/ws") as ws:  # pragma: no cover - websocket
            await ws.send(json.dumps(estado))
            data = await ws.recv()
            return json.loads(data)
    def registrar_modulo(self, nombre: str, metadata: Dict[str, Any]) -> Any:
        """Registra un módulo en el QualiaHub remoto."""
        url = f"{self.base_url}/register"
        payload = {"name": nombre, "metadata": metadata}
        return self.session.post(url, json=payload)

    def consultar_modulos(self) -> Dict[str, Any]:
        """Obtiene la lista de módulos registrados."""
        url = f"{self.base_url}/modules"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def difundir_evento(self, evento: str) -> Any:
        """Difunde un evento a través del hub."""
        url = f"{self.base_url}/event"
        payload = {"event": evento}
        return self.session.post(url, json=payload)
