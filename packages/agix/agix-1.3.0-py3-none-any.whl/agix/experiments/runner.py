import inspect
from typing import Iterable, List, Callable

import pandas as pd

from agix.evaluation.metrics import EvaluationMetrics


class ExperimentRunner:
    """Ejecuta experimentos con múltiples agentes y entornos."""

    def __init__(
        self,
        agents: Iterable,
        environments: Iterable,
        metrics: Iterable[Callable] | None = None,
    ) -> None:
        self.agents = list(agents)
        self.environments = list(environments)
        if metrics is None:
            metrics = [
                EvaluationMetrics.average_reward,
                EvaluationMetrics.max_reward,
                EvaluationMetrics.std_reward,
                EvaluationMetrics.success_rate,
            ]
        self.metrics = list(metrics)

    def _run_episode(self, agent, env) -> float:
        obs = env.reset()
        done = False
        total_reward = 0.0
        while not done:
            if hasattr(agent, "perceive"):
                agent.perceive(obs)
            if hasattr(agent, "decide"):
                action = agent.decide()
            else:
                action = 0
            obs, reward, done, _ = env.step(action)
            if hasattr(agent, "learn"):
                agent.learn(reward, done)
            total_reward += reward
        if hasattr(agent, "reset"):
            agent.reset()
        return total_reward

    def run(self, episodes: int = 1) -> pd.DataFrame:
        """Ejecuta todas las combinaciones y devuelve un DataFrame."""
        results: List[dict] = []
        for agent in self.agents:
            for env in self.environments:
                rewards = [self._run_episode(agent, env) for _ in range(episodes)]
                row = {
                    "agent": agent.__class__.__name__,
                    "environment": env.__class__.__name__,
                }
                for metric in self.metrics:
                    func = metric
                    name = func.__name__
                    try:
                        value = func(rewards)
                    except Exception:
                        try:
                            value = func(agent, [env])
                        except Exception:
                            value = None
                    row[name] = value
                results.append(row)
        return pd.DataFrame(results)
