"""Configuración sencilla para elegir modelos de aprendizaje."""

from src.agix.learning.ml.sklearn_wrapper import SklearnLearner

MODEL_REGISTRY = {
    "sklearn": SklearnLearner,
}

DEFAULT_MODEL = "sklearn"
