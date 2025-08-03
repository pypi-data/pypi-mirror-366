# src/agix/cli/commands/inspect.py

import argparse
from typing import Optional

from agix.evaluation.self_organization_eval import run as run_self_org
from agix.identity.self_model import SelfModel


def run_inspection(args):
    """Inspecciona y muestra el estado interno reflexivo del agente."""

    if getattr(args, "self_org", False):
        inspect_self_org(args)
        return

    # Crear un modelo de ejemplo o cargar uno real
    self_model = SelfModel(agent_name=args.name, version=args.version)

    # Registrar módulos de ejemplo (esto sería dinámico en tu sistema real)
    self_model.register_module("perception", "Módulo de percepción visual")
    self_model.register_module("reasoning", "Razonamiento simbólico-latente")
    self_model.update_state("energía", 0.82)
    self_model.update_state("fatiga", 0.15)

    # Mostrar introspección
    print("\n🧠 Estado Interno del Agente:\n")
    introspection = self_model.introspect()

    print(f"Identidad   : {introspection['identity']}")
    print(f"Módulos     : {introspection['modules']}")
    print(f"Estado      : {introspection['state']}")
    print(f"Autoquery   : {self_model.generate_self_query()}")


def inspect_self_org(args):
    """Muestra el puntaje de auto-organización y la proto-agencia."""

    self_model = SelfModel(agent_name=args.name, version=args.version)
    scores = run_self_org(num_scenarios=3)
    average = sum(scores) / len(scores) if scores else 0.0
    self_model.update_self_organization(average)

    print("\n🧩 Auto-organización del Agente:\n")
    print(f"self_organization_score: {self_model.self_organization_score:.3f}")
    print(f"proto_agency           : {self_model.proto_agency}")


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """Devuelve el parser configurado para ``inspect``.

    Si ``parser`` es ``None`` se crea uno nuevo.
    """

    if parser is None:
        parser = argparse.ArgumentParser(
            description="Inspecciona el estado reflexivo del agente AGI"
        )

    parser.add_argument(
        "--name", type=str, default="AGI-Core", help="Nombre del agente"
    )
    parser.add_argument(
        "--version", type=str, default="0.3.0", help="Versión del agente"
    )
    parser.add_argument(
        "--self-org",
        action="store_true",
        help="Muestra puntaje de auto-organización y proto-agencia",
    )

    return parser
