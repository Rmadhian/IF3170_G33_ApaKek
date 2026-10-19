import unittest

from core.objective import (
    floating_count,
    fragile_support_count,
    overlap_volume,
    total_overlap,
)


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


class TestFloating(unittest.TestCase):
    def test_on_floor(self):
        self.assertEqual(floating_count([(0, 0, 0, 2, 2, 2)]), 0)

    def test_in_air(self):
        self.assertEqual(floating_count([(0, 0, 3, 2, 2, 2)]), 1)

    def test_stacked(self):
        boxes = [(0, 0, 0, 2, 2, 2), (0, 0, 2, 2, 2, 2)]
        self.assertEqual(floating_count(boxes), 0)

    def test_partial_support(self):
        boxes = [(0, 0, 0, 2, 2, 2), (1, 1, 2, 2, 2, 2)]
        self.assertEqual(floating_count(boxes), 0)

    def test_gap_below(self):
        boxes = [(0, 0, 0, 2, 2, 2), (0, 0, 3, 2, 2, 2)]
        self.assertEqual(floating_count(boxes), 1)

    def test_edge_touch_only(self):
        boxes = [(0, 0, 0, 2, 2, 2), (2, 0, 2, 2, 2, 2)]
        self.assertEqual(floating_count(boxes), 1)

    def test_identical_boxes(self):
        boxes = [(0, 0, 2, 2, 2, 2), (0, 0, 2, 2, 2, 2)]
        self.assertEqual(floating_count(boxes), 2)


class TestFragile(unittest.TestCase):
    def test_fragile_alone(self):
        self.assertEqual(fragile_support_count([(0, 0, 0, 2, 2, 2)], [True]), 0)

    def test_on_top_of_fragile(self):
        boxes = [(0, 0, 0, 2, 2, 2), (0, 0, 2, 2, 2, 2)]
        self.assertEqual(fragile_support_count(boxes, [True, False]), 1)

    def test_fragile_on_top(self):
        boxes = [(0, 0, 0, 2, 2, 2), (0, 0, 2, 2, 2, 2)]
        self.assertEqual(fragile_support_count(boxes, [False, True]), 0)

    def test_two_on_fragile(self):
        boxes = [(0, 0, 0, 4, 2, 2), (0, 0, 2, 2, 2, 1), (2, 0, 2, 2, 2, 1)]
        self.assertEqual(fragile_support_count(boxes, [True, False, False]), 2)

    def test_side_by_side(self):
        boxes = [(0, 0, 0, 2, 2, 2), (2, 0, 0, 2, 2, 2)]
        self.assertEqual(fragile_support_count(boxes, [True, False]), 0)

    def test_gap_above_fragile(self):
        boxes = [(0, 0, 0, 2, 2, 2), (0, 0, 3, 2, 2, 2)]
        self.assertEqual(fragile_support_count(boxes, [True, False]), 0)


if __name__ == "__main__":
    unittest.main()
