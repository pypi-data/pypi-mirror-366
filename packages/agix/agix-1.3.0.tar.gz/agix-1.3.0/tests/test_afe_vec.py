import unittest

from src.agix.qualia.affective_vector import AffectiveVector


class TestAffectiveVector(unittest.TestCase):
    def test_roundtrip(self):
        data = {"alegria": 0.7, "miedo": 0.3}
        vec = AffectiveVector.from_dict(data)
        self.assertEqual(vec.to_dict(), data)


if __name__ == "__main__":
    unittest.main()
