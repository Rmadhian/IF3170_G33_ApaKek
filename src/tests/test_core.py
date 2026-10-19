import unittest

from core.objective import (
    floating_count,
    objective,
    violations,
    fragile_support_count,
    out_of_bounds_volume,
    overweight,
    overlap_volume,
    total_out_of_bounds,
    total_overlap,
)
from core.models import Package, Placement, State, Truck


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


class TestEdgeCases(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(total_overlap([]), 0)
        self.assertEqual(floating_count([]), 0)
        self.assertEqual(fragile_support_count([], []), 0)

    def test_overlap_symmetric(self):
        a, b = (0, 0, 0, 3, 2, 1), (1, 1, 0, 3, 3, 3)
        self.assertEqual(overlap_volume(a, b), overlap_volume(b, a))

    def test_supported_by_two(self):
        boxes = [(0, 0, 0, 1, 2, 2), (1, 0, 0, 1, 2, 2), (0, 0, 2, 2, 2, 1)]
        self.assertEqual(floating_count(boxes), 0)

    def test_fragile_still_supports_physically(self):
        boxes = [(0, 0, 0, 2, 2, 2), (0, 0, 2, 2, 2, 2)]
        self.assertEqual(floating_count(boxes), 0)
        self.assertEqual(fragile_support_count(boxes, [True, False]), 1)

    def test_tower(self):
        boxes = [(0, 0, 0, 2, 2, 1), (0, 0, 1, 2, 2, 1), (0, 0, 2, 2, 2, 1)]
        self.assertEqual(floating_count(boxes), 0)
        self.assertEqual(fragile_support_count(boxes, [False, True, False]), 1)

    def test_overlapping_and_floating(self):
        boxes = [(0, 0, 1, 2, 2, 2), (1, 1, 1, 2, 2, 2)]
        self.assertEqual(total_overlap(boxes), 2)
        self.assertEqual(floating_count(boxes), 2)


class TestModels(unittest.TestCase):
    def test_cube_one_orientation(self):
        self.assertEqual(len(Package("A", 2, 2, 2, 10, 1).orientations()), 1)

    def test_box_orientations(self):
        self.assertEqual(len(Package("A", 1, 2, 3, 10, 1).orientations()), 6)

    def test_box_uses_orientation(self):
        pkgs = [Package("A", 1, 2, 3, 10, 1)]
        state = State([Placement(True, 4, 5, 0, 2)])
        self.assertEqual(state.box(0, pkgs), (4, 5, 0, 2, 1, 3))

    def test_copy_independent(self):
        state = State([Placement(True, 0, 0, 0, 0)])
        clone = state.copy()
        clone.placements[0].x = 9
        self.assertEqual(state.placements[0].x, 0)

    def test_inside_indices(self):
        state = State([Placement(True, 0, 0, 0), Placement(False), Placement(True, 2, 0, 0)])
        self.assertEqual(state.inside_indices(), [0, 2])


class TestBoundsWeight(unittest.TestCase):
    truck = (10, 10, 10)

    def test_fully_inside(self):
        self.assertEqual(out_of_bounds_volume((0, 0, 0, 10, 10, 10), self.truck), 0)

    def test_partly_outside(self):
        self.assertEqual(out_of_bounds_volume((9, 0, 0, 2, 1, 1), self.truck), 1)

    def test_negative_coord(self):
        self.assertEqual(out_of_bounds_volume((-1, 0, 0, 2, 2, 2), self.truck), 4)

    def test_fully_outside(self):
        self.assertEqual(out_of_bounds_volume((20, 0, 0, 2, 2, 2), self.truck), 8)

    def test_total(self):
        boxes = [(0, 0, 0, 1, 1, 1), (9, 9, 9, 2, 2, 2)]
        self.assertEqual(total_out_of_bounds(boxes, self.truck), 7)

    def test_under_capacity(self):
        self.assertEqual(overweight(80, 100), 0)

    def test_exact_capacity(self):
        self.assertEqual(overweight(100, 100), 0)

    def test_over_capacity(self):
        self.assertEqual(overweight(130, 100), 30)


class TestObjective(unittest.TestCase):
    truck = Truck(4, 4, 4, 10)
    pkgs = [Package("A", 2, 2, 2, 30, 4), Package("B", 2, 2, 2, 20, 4, True)]

    def test_empty_truck(self):
        state = State([Placement(False), Placement(False)])
        self.assertEqual(objective(state, self.pkgs, self.truck), 0)

    def test_valid_side_by_side(self):
        state = State([Placement(True, 0, 0, 0), Placement(True, 2, 0, 0)])
        self.assertEqual(objective(state, self.pkgs, self.truck), 50)

    def test_outside_ignored(self):
        state = State([Placement(True, 0, 0, 0), Placement(False)])
        self.assertEqual(objective(state, self.pkgs, self.truck), 30)

    def test_overlap_penalized(self):
        state = State([Placement(True, 0, 0, 0), Placement(True, 1, 0, 0)])
        self.assertEqual(violations(state, self.pkgs, self.truck)["overlap"], 4)
        self.assertEqual(objective(state, self.pkgs, self.truck), 50 - 51 * 4)

    def test_on_fragile_penalized(self):
        state = State([Placement(True, 0, 0, 2), Placement(True, 0, 0, 0)])
        v = violations(state, self.pkgs, self.truck)
        self.assertEqual((v["fragile"], v["floating"]), (1, 0))

    def test_overweight_penalized(self):
        heavy = [Package("A", 1, 1, 1, 30, 8), Package("B", 1, 1, 1, 20, 8)]
        state = State([Placement(True, 0, 0, 0), Placement(True, 1, 0, 0)])
        self.assertEqual(violations(state, heavy, self.truck)["overweight"], 6)

    def test_valid_beats_invalid(self):
        valid = State([Placement(True, 0, 0, 0), Placement(False)])
        invalid = State([Placement(True, 0, 0, 0), Placement(True, 0, 0, 3)])
        self.assertGreater(objective(valid, self.pkgs, self.truck),
                           objective(invalid, self.pkgs, self.truck))


if __name__ == "__main__":
    unittest.main()
