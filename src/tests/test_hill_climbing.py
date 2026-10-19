import random
import unittest

from core.models import Package, Placement, State, Truck, random_state
from core.objective import objective, violations
from hillClimbing.hillClimbing import sideways_move, steepest_ascent, stochastic


class TestRandomState(unittest.TestCase):
    def test_inside_within_truck(self):
        truck = Truck(5, 5, 5, 100)
        pkgs = [Package(str(i), 2, 3, 1, 10, 1) for i in range(10)]
        state = random_state(pkgs, truck, random.Random(1))
        self.assertEqual(violations(state, pkgs, truck)["out_of_bounds"], 0)

    def test_too_big_stays_outside(self):
        truck = Truck(2, 2, 2, 100)
        pkgs = [Package("A", 5, 5, 5, 10, 1)]
        state = random_state(pkgs, truck, random.Random(1))
        self.assertFalse(state.placements[0].inside)


class TestSteepestAscent(unittest.TestCase):
    truck = Truck(4, 4, 4, 100)
    pkgs = [Package("A", 2, 2, 2, 30, 4), Package("B", 2, 2, 2, 20, 4, True),
            Package("C", 4, 4, 1, 15, 4)]

    def test_history_increasing(self):
        result = steepest_ascent(self.pkgs, self.truck, seed=3)
        h = result["history"]
        self.assertTrue(all(a < b for a, b in zip(h, h[1:])))

    def test_fixes_invalid_start(self):
        start = State([Placement(True, 0, 0, 2), Placement(True, 1, 1, 2), Placement(False)])
        result = steepest_ascent(self.pkgs, self.truck, initial=start)
        v = violations(result["final_state"], self.pkgs, self.truck)
        self.assertEqual(sum(v.values()), 0)

    def test_initial_not_modified(self):
        start = State([Placement(False), Placement(False), Placement(False)])
        steepest_ascent(self.pkgs, self.truck, initial=start)
        self.assertFalse(start.placements[0].inside)

    def test_final_matches_objective(self):
        result = steepest_ascent(self.pkgs, self.truck, seed=5)
        self.assertEqual(result["final_objective"],
                         objective(result["final_state"], self.pkgs, self.truck))

    def test_same_seed_same_result(self):
        a = steepest_ascent(self.pkgs, self.truck, seed=7)
        b = steepest_ascent(self.pkgs, self.truck, seed=7)
        self.assertEqual(a["history"], b["history"])


class TestSidewaysMove(unittest.TestCase):
    truck = Truck(4, 4, 4, 100)
    pkgs = [Package("A", 2, 2, 2, 30, 4), Package("B", 2, 2, 2, 20, 4, True),
            Package("C", 4, 4, 1, 15, 4)]

    def test_never_decreases(self):
        h = sideways_move(self.pkgs, self.truck, max_sideways=10, seed=3)["history"]
        self.assertTrue(all(a <= b for a, b in zip(h, h[1:])))

    def test_zero_limit_is_steepest(self):
        r = sideways_move(self.pkgs, self.truck, max_sideways=0, seed=3)
        self.assertEqual(r["sideways_moves"], 0)
        h = r["history"]
        self.assertTrue(all(a < b for a, b in zip(h, h[1:])))

    def test_total_limit(self):
        limit = 5
        r = sideways_move(self.pkgs, self.truck, max_sideways=limit, seed=3)
        flat = sum(1 for a, b in zip(r["history"], r["history"][1:]) if a == b)
        self.assertLessEqual(r["sideways_moves"], limit)
        self.assertEqual(flat, r["sideways_moves"])

    def test_flat_start_moves_sideways(self):
        start = State([Placement(True, 0, 0, 0), Placement(False), Placement(False)])
        tiny = Truck(2, 2, 2, 100)
        r = sideways_move(self.pkgs, tiny, max_sideways=3, initial=start, seed=1)
        self.assertEqual(r["sideways_moves"], 3)
        self.assertEqual(r["final_objective"], 30)


class TestStochastic(unittest.TestCase):
    truck = Truck(4, 4, 4, 100)
    pkgs = [Package("A", 2, 2, 2, 30, 4), Package("B", 2, 2, 2, 20, 4, True),
            Package("C", 4, 4, 1, 15, 4)]

    def test_runs_max_iter(self):
        r = stochastic(self.pkgs, self.truck, max_iter=50, seed=1)
        self.assertEqual(r["iterations"], 50)
        self.assertEqual(len(r["history"]), 51)

    def test_never_decreases(self):
        h = stochastic(self.pkgs, self.truck, max_iter=200, seed=2)["history"]
        self.assertTrue(all(a <= b for a, b in zip(h, h[1:])))

    def test_improves_from_empty(self):
        start = State([Placement(False), Placement(False), Placement(False)])
        r = stochastic(self.pkgs, self.truck, max_iter=300, initial=start, seed=4)
        self.assertGreater(r["final_objective"], 0)

    def test_same_seed_same_result(self):
        a = stochastic(self.pkgs, self.truck, max_iter=100, seed=9)
        b = stochastic(self.pkgs, self.truck, max_iter=100, seed=9)
        self.assertEqual(a["history"], b["history"])


if __name__ == "__main__":
    unittest.main()
