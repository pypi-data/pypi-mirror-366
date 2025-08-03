import unittest

from src.agix.ethics.moral_emotions import MoralEmotionSimulator


class TestMoralEmotionSimulator(unittest.TestCase):
    def test_update_and_reset(self):
        sim = MoralEmotionSimulator()
        self.assertEqual(
            sim.estado(), {"culpa": 0.0, "remordimiento": 0.0, "satisfaccion": 0.0}
        )

        sim.actualizar("positivo")
        self.assertAlmostEqual(sim.estado()["satisfaccion"], 0.1)
        self.assertAlmostEqual(sim.estado()["culpa"], 0.0)

        sim.actualizar("negativo")
        estado = sim.estado()
        self.assertAlmostEqual(estado["culpa"], 0.1)
        self.assertAlmostEqual(estado["remordimiento"], 0.1)
        self.assertAlmostEqual(estado["satisfaccion"], 0.0)

        sim.reiniciar()
        self.assertEqual(
            sim.estado(), {"culpa": 0.0, "remordimiento": 0.0, "satisfaccion": 0.0}
        )


if __name__ == "__main__":
    unittest.main()
