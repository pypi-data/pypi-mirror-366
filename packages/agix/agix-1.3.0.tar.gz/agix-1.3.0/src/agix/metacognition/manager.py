from src.agix.identity.self_model import SelfModel
from src.agix.control.reflexive_logic import ReflexiveLogic
from src.agix.metacognition.self_organization import SelfOrganizationMonitor
import time


class MetacognitionManager:
    """Coordina el modelo reflexivo y la evaluación de decisiones."""

    def __init__(self, agent_name: str = "AGI-Core", version: str = "1.1.0") -> None:
        self.self_model = SelfModel(agent_name=agent_name, version=version)
        self.logic = ReflexiveLogic()
        self.self_organization = SelfOrganizationMonitor()

    def observe_decision(self, context: dict, action: str, result: dict) -> None:
        """Registra una acción y su resultado para análisis posterior."""
        self.logic.registrar_evento(context, action, result)
        # Actualiza información de auto-organización
        modules = context.get("active_modules")
        if modules:
            self.self_organization.active_modules.extend(modules)
        dependencies = context.get("dependencies")
        if dependencies:
            for mod, deps in dependencies.items():
                self.self_organization.dependencies.setdefault(mod, [])
                self.self_organization.dependencies[mod].extend(deps)
        self.self_organization.activation_times.append(time.time())

        score = self.self_organization.compute_score()
        self.self_model.update_self_organization(score)

    def self_assess(self) -> float | None:
        """Evalúa la coherencia de las decisiones observadas."""
        coherence = self.logic.evaluar_coherencia()
        self.self_model.update_state("coherence", coherence)
        return coherence

    @property
    def proto_agency(self) -> bool:
        """Indica si el agente ha alcanzado el estado de proto-agencia."""
        return self.self_model.proto_agency
