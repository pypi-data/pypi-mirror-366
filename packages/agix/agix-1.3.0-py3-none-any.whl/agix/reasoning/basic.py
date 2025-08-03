from typing import List, Dict, Optional


class Reasoner:
    """
    Selecciona el modelo óptimo basado en precisión e interpretabilidad.
    Útil para elegir entre múltiples modelos evaluados bajo criterios cuantitativos.
    """

    def select_best_model(self, evaluations: List[Dict]) -> Dict[str, Optional[str | float]]:
        if not evaluations:
            return {
                "name": None,
                "accuracy": 0.0,
                "reason": "No se proporcionaron modelos para evaluar."
            }

        # Ordenar por precisión descendente
        evaluations_sorted = sorted(evaluations, key=lambda m: m.get("accuracy", 0.0), reverse=True)
        best_accuracy = evaluations_sorted[0]["accuracy"]

        # Filtrar modelos con mejor precisión
        candidates = [m for m in evaluations_sorted if m.get("accuracy") == best_accuracy]

        # Elegir el más interpretable entre ellos
        final = sorted(candidates, key=lambda m: m.get("interpretability", 0.0), reverse=True)[0]

        reason = (
            f"Modelo seleccionado: '{final['name']}'\n"
            f"- Precisión: {final['accuracy']:.2f}\n"
            f"- Interpretabilidad: {final['interpretability']:.2f}"
        )

        return {
            "name": final.get("name"),
            "accuracy": final.get("accuracy"),
            "reason": reason
        }
