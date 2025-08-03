# src/agix/cli/commands/experiment.py

"""Subcomando para ejecutar experimentos comparativos."""

import argparse
from typing import Optional

from agix.cli.commands.simulate import ToyEnvironment
from agix.agents.genetic import GeneticAgent
from agix.experiments import ExperimentRunner
from agix.evaluation.metrics import EvaluationMetrics
from agix.environments import VideoGameEnvironment, VREnvironment, RobotEnvironment

# Mapeo simple de agentes y entornos disponibles
AGENTS = {
    "genetic": GeneticAgent,
    "geneticagent": GeneticAgent,
}

ENVS = {
    "dummy": ToyEnvironment,
    "toyenv": ToyEnvironment,
    "videogame": VideoGameEnvironment,
    "vr": VREnvironment,
    "robot": RobotEnvironment,
}


def run_experiment(args):
    agent_cls = AGENTS.get(args.agent_class.lower())
    env_cls = ENVS.get(args.env_class.lower())
    if not agent_cls or not env_cls:
        print("❌ Agente o entorno no reconocidos.")
        return

    agents = [agent_cls(action_space_size=4) for _ in range(args.num_agents)]
    envs = [env_cls() for _ in range(args.num_envs)]
    metrics = [
        EvaluationMetrics.average_reward,
        EvaluationMetrics.max_reward,
        EvaluationMetrics.std_reward,
        EvaluationMetrics.success_rate,
    ]

    runner = ExperimentRunner(agents, envs, metrics)
    df = runner.run(episodes=args.episodes)
    print("\n📊 Resultados del experimento:\n")
    print(df.to_string(index=False))


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser(description="Ejecuta experimentos comparativos")

    parser.add_argument("--agent-class", required=True, help="Clase de agente")
    parser.add_argument("--env-class", required=True, help="Clase de entorno")
    parser.add_argument("--num-agents", type=int, default=1, help="Número de agentes")
    parser.add_argument("--num-envs", type=int, default=1, help="Número de entornos")
    parser.add_argument("--episodes", type=int, default=1, help="Episodios por entorno")
    return parser

__all__ = ["run_experiment", "build_parser"]
