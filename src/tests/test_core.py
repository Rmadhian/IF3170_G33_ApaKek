import unittest

from core.objective import overlap_volume, total_overlap


class TestOverlap(unittest.TestCase):
    def test_no_overlap(self):
        self.assertEqual(overlap_volume((0, 0, 0, 2, 2, 2), (5, 5, 5, 1, 1, 1)), 0)

    def test_touching_face(self):
        self.assertEqual(overlap_volume((0, 0, 0, 2, 2, 2), (2, 0, 0, 2, 2, 2)), 0)

    def test_partial(self):
        self.assertEqual(overlap_volume((0, 0, 0, 2, 2, 2), (1, 1, 1, 2, 2, 2)), 1)

    def test_contained(self):
        self.assertEqual(overlap_volume((0, 0, 0, 4, 4, 4), (1, 1, 1, 2, 2, 2)), 8)

    def test_total(self):
        boxes = [(0, 0, 0, 2, 2, 2), (1, 0, 0, 2, 2, 2), (10, 10, 10, 1, 1, 1)]
        self.assertEqual(total_overlap(boxes), 4)


if __name__ == "__main__":
    unittest.main()
