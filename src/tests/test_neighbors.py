import random
import unittest

from core.models import Package, Placement, State, Truck
from core.neighbors import (
    all_neighbors,
    candidate_positions,
    move,
    random_neighbor,
    rotate,
    swap,
)


class TestNeighbors(unittest.TestCase):
    truck = Truck(4, 4, 4, 100)
    pkgs = [Package("A", 1, 2, 3, 10, 1), Package("B", 2, 2, 2, 20, 1)]

    def state(self):
        return State([Placement(True, 0, 0, 0, 0), Placement(False)])

    def test_swap_in_out(self):
        new = swap(self.state(), 0, 1)
        self.assertFalse(new.placements[0].inside)
        self.assertEqual((new.placements[1].inside, new.placements[1].x), (True, 0))

    def test_swap_keeps_original(self):
        s = self.state()
        swap(s, 0, 1)
        self.assertTrue(s.placements[0].inside)

    def test_move_to_coord(self):
        new = move(self.state(), 1, (2, 2, 0))
        p = new.placements[1]
        self.assertEqual((p.inside, p.x, p.y, p.z), (True, 2, 2, 0))

    def test_move_out(self):
        self.assertFalse(move(self.state(), 0, None).placements[0].inside)

    def test_rotate_z(self):
        new = rotate(self.state(), 0, "z", self.pkgs)
        self.assertEqual(new.dims(0, self.pkgs), (2, 1, 3))

    def test_rotate_x(self):
        new = rotate(self.state(), 0, "x", self.pkgs)
        self.assertEqual(new.dims(0, self.pkgs), (1, 3, 2))

    def test_rotate_twice_back(self):
        s = self.state()
        twice = rotate(rotate(s, 0, "y", self.pkgs), 0, "y", self.pkgs)
        self.assertEqual(twice.dims(0, self.pkgs), s.dims(0, self.pkgs))

    def test_candidates_inside_truck(self):
        for x, y, z in candidate_positions(self.state(), 1, self.pkgs, self.truck):
            self.assertTrue(x + 2 <= 4 and y + 2 <= 4 and z + 2 <= 4)

    def test_candidates_next_to_box(self):
        spots = candidate_positions(self.state(), 1, self.pkgs, self.truck)
        self.assertIn((1, 0, 0), spots)
        self.assertIn((0, 2, 0), spots)

    def test_all_neighbors_differ(self):
        s = self.state()
        for new in all_neighbors(s, self.pkgs, self.truck):
            self.assertNotEqual(new, s)

    def test_random_neighbor_valid_index(self):
        rng = random.Random(0)
        s = self.state()
        for _ in range(50):
            new = random_neighbor(s, self.pkgs, self.truck, rng)
            for i, p in enumerate(new.placements):
                n = len(self.pkgs[i].orientations())
                self.assertTrue(0 <= p.orientation < n)


if __name__ == "__main__":
    unittest.main()
