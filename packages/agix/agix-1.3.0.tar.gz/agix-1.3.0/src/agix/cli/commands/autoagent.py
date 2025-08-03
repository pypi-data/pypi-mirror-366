import argparse
from typing import Optional

from agix.agents.genetic import GeneticAgent
from agix.autoagent import AutoAgent
from agix.cli.commands.simulate import ToyEnvironment


def run_autoagent(args: argparse.Namespace) -> None:
    """Ejecuta el bucle principal de :class:`AutoAgent`."""
    agent = GeneticAgent(action_space_size=args.actions)
    env = ToyEnvironment(obs_size=args.observations)
    loop = AutoAgent(agent, env)

    print("\n🚀 Ejecutando AutoAgent...\n")
    metrics = loop.run(episodes=1, max_steps=args.steps)
    total = sum(loop.reward_history)
    print(f"Recompensa total: {total:.2f}")
    print(f"Métricas: {metrics}")


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """Construye el parser para ``autoagent``."""
    if parser is None:
        parser = argparse.ArgumentParser(description="Lanza el bucle AutoAgent")

    parser.add_argument(
        "--observations",
        type=int,
        default=10,
        help="Tamaño del vector de observación",
    )
    parser.add_argument(
        "--actions",
        type=int,
        default=4,
        help="Número de acciones posibles",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=5,
        help="Número máximo de pasos por episodio",
    )
    return parser


__all__ = ["run_autoagent", "build_parser"]
