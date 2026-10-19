import json
import os
import tempfile
import unittest

from simulatedAnnealing.simulatedAnnealing import run_sa
from core.io import load_input, snapshot
from core.models import Package, Placement, State, Truck


class TestIO(unittest.TestCase):
    def test_load_input(self):
        data = {"truck": {"w": 4, "l": 5, "h": 6, "max_capacity": 50},
                "packages": [{"id": "A", "w": 1, "l": 2, "h": 3, "value": 10, "weight": 2, "fragile": True},
                             {"id": "B", "w": 2, "l": 2, "h": 2, "value": 5, "weight": 1}]}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "input.json")
            with open(path, "w") as f:
                json.dump(data, f)
            packages, truck = load_input(path)
        self.assertEqual(truck, Truck(4, 5, 6, 50))
        self.assertTrue(packages[0].fragile)
        self.assertFalse(packages[1].fragile)

    def test_snapshot(self):
        pkgs = [Package("A", 1, 2, 3, 10, 2, True), Package("B", 2, 2, 2, 5, 1)]
        state = State([Placement(True, 1, 0, 0, 2), Placement(False)])
        rows = snapshot(state, pkgs)
        self.assertEqual((rows[0]["x"], rows[0]["w"], rows[0]["l"]), (1, 2, 1))
        self.assertTrue(rows[0]["is_fragile"])
        self.assertEqual((rows[1]["in_truck"], rows[1]["x"]), (False, None))


class TestSA(unittest.TestCase):
    truck = Truck(4, 4, 4, 100)
    pkgs = [Package("A", 2, 2, 2, 30, 4), Package("B", 2, 2, 2, 20, 4, True)]

    def test_run_sa(self):
        r = run_sa(self.pkgs, self.truck, seed=1, max_iterations=300)
        self.assertGreaterEqual(r.best_score, r.initial_score)
        self.assertEqual(len(r.objective_history), r.iterations + 1)

    def test_same_seed_same_result(self):
        a = run_sa(self.pkgs, self.truck, seed=4, max_iterations=200)
        b = run_sa(self.pkgs, self.truck, seed=4, max_iterations=200)
        self.assertEqual(a.objective_history, b.objective_history)


if __name__ == "__main__":
    unittest.main()
