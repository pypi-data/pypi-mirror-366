"""Subpaquete de procesos cualitativos y estado emocional."""

__all__ = [
    "ConceptClassifier",
    "HeuristicQualiaSpirit",
    "EmotionalRNN",
    "QualiaMiddleware",
]


def __getattr__(name):
    if name == "ConceptClassifier":
        from .concept_classifier import ConceptClassifier
        return ConceptClassifier
    if name == "HeuristicQualiaSpirit":
        from .heuristic_spirit import HeuristicQualiaSpirit
        return HeuristicQualiaSpirit
    if name == "EmotionalRNN":
        from .emotional_rnn import EmotionalRNN
        return EmotionalRNN
    if name == "QualiaMiddleware":
        from .middleware import QualiaMiddleware
        return QualiaMiddleware
    raise AttributeError(name)
