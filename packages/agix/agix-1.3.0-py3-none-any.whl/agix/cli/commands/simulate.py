# src/agix/cli/commands/simulate.py

import argparse
from typing import Optional
import numpy as np

from agix.agents.genetic import GeneticAgent
from agix.environments import (
    VideoGameEnvironment,
    VREnvironment,
    RobotEnvironment,
)


class ToyEnvironment:
    """Entorno mínimo para simulaciones desde CLI"""

    def __init__(self, obs_size=10):
        self.obs_size = obs_size
        self.steps = 0
        self.max_steps = 5

    def reset(self):
        self.steps = 0
        return np.ones(self.obs_size)

    def step(self, action):
        self.steps += 1
        reward = 1.0 if action < 2 else -0.5
        done = self.steps >= self.max_steps
        return np.ones(self.obs_size), reward, done, {}


def run_simulation(args):
    """
    Ejecuta una simulación básica de un agente en un entorno controlado.
    """
    agent = GeneticAgent(action_space_size=args.actions)

    env_map = {
        "toy": ToyEnvironment,
        "videogame": VideoGameEnvironment,
        "vr": VREnvironment,
        "robot": RobotEnvironment,
    }
    env_cls = env_map.get(args.env_class.lower(), ToyEnvironment)
    env = env_cls(obs_size=args.observations)

    obs = env.reset()
    total_reward = 0

    print("\n🤖 Iniciando simulación...\n")
    for step in range(env.max_steps):
        agent.perceive(obs)
        action = agent.decide()
        obs, reward, done, _ = env.step(action)
        agent.learn(reward)

        print(f"Paso {step+1} | Acción: {action} | Recompensa: {reward:.2f}")
        total_reward += reward

        if done:
            break

    print(f"\n🎯 Simulación finalizada. Recompensa total: {total_reward:.2f}")


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """Construye el parser para el subcomando ``simulate``.

    Si se proporciona ``parser`` se añaden los argumentos sobre él, de lo
    contrario se crea un ``ArgumentParser`` independiente.
    """

    if parser is None:
        parser = argparse.ArgumentParser(
            description="Simula un agente AGI simple en un entorno mínimo"
        )

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
        "--env-class",
        default="toy",
        help="Tipo de entorno (toy, videogame, vr, robot)",
    )

    return parser
