import unittest

from src.agix.qualia.heuristic_spirit import HeuristicQualiaSpirit
from src.agix.qualia.affective_vector import AffectiveVector


class TestHeuristicQualiaSpirit(unittest.TestCase):
    def test_registra_emociones_con_reglas(self):
        spirit = HeuristicQualiaSpirit()

        def regla(emocion, carga):
            return "alegria", carga * 0.5

        spirit.add_rule(regla)
        spirit.experimentar("lluvia de estrellas", 0.8, "sorpresa")
        diario = spirit.diario()
        self.assertEqual(diario[-1][1], "alegria")
        self.assertAlmostEqual(diario[-1][2], 0.4, places=3)

    def test_interactua_con_affective_vector(self):
        spirit = HeuristicQualiaSpirit()
        spirit.experimentar("cancion", 0.7, "alegria")
        vec = spirit.to_affective_vector()
        nombre = "fused_alegria_cancion"
        self.assertIn(nombre, vec.values)

        nuevo = AffectiveVector.from_dict({"tristeza": 1.0})
        spirit.from_affective_vector(nuevo)
        self.assertIn("tristeza", spirit.estado_emocional.emociones)
        self.assertAlmostEqual(spirit.estado_emocional.emociones["tristeza"], 1.0)

    def test_flujo_con_rnn(self):
        spirit = HeuristicQualiaSpirit()
        spirit.experimentar("saludo", 0.5, "alegria")
        spirit.experimentar("chiste", 0.6, "alegria")
        pred = spirit.predecir_futuro()
        if pred:
            self.assertTrue(all(isinstance(v, float) for v in pred.values()))


if __name__ == "__main__":
    unittest.main()
