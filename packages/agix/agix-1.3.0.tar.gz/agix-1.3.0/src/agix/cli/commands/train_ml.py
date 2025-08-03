# src/agix/cli/commands/train_ml.py
"""Subcomando para entrenar modelos de aprendizaje automático."""

import argparse
from typing import Optional

import numpy as np
from sklearn.linear_model import SGDClassifier

from src.agix.config import MODEL_REGISTRY, DEFAULT_MODEL


def run_training(args: argparse.Namespace) -> None:
    """Entrena un modelo simple de ML según la configuración."""
    model_key = args.model or DEFAULT_MODEL
    model_key = model_key.lower()
    learner_cls = MODEL_REGISTRY.get(model_key)
    if learner_cls is None:
        print(f"Modelo '{model_key}' no reconocido. Opciones: {list(MODEL_REGISTRY.keys())}")
        return

    estimator = SGDClassifier(max_iter=5)
    learner = learner_cls(estimator)

    X = np.array([[0], [1], [2], [3]])
    y = np.array([0, 0, 1, 1])

    if args.incremental:
        learner.train_incremental(X, y, classes=np.array([0, 1]))
    else:
        learner.train(X, y)

    preds = learner.predict(X)
    print(f"Predicciones: {preds.tolist()}")


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """Construye el parser para ``train_ml``."""
    if parser is None:
        parser = argparse.ArgumentParser(description="Entrena un modelo de ML")

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help="Nombre del modelo definido en config.py",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Usar entrenamiento incremental si el modelo lo permite",
    )

    return parser


__all__ = ["run_training", "build_parser"]
