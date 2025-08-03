"""Componentes de metacognición para AGIX."""

from .self_organization import SelfOrganizationMonitor

try:  # pragma: no cover - dependencias opcionales
    from .manager import MetacognitionManager
    from .dynamic_evaluator import DynamicMetaEvaluator
    __all__ = [
        "MetacognitionManager",
        "DynamicMetaEvaluator",
        "SelfOrganizationMonitor",
    ]
except Exception:  # noqa: BLE001
    __all__ = ["SelfOrganizationMonitor"]
