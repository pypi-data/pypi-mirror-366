"""Herramientas de bloqueo y verificación de comandos."""

from __future__ import annotations

FORBIDDEN_PATTERNS = [
    "import os",
    "import sys",
    "import subprocess",
    "os.system",
    "subprocess.Popen",
    "eval(",
    "exec(",
]


def verificar(texto: str) -> bool:
    """Devuelve ``True`` si el texto no contiene patrones prohibidos."""
    lower = texto.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in lower:
            return False
    return True

__all__ = ["FORBIDDEN_PATTERNS", "verificar"]
