from __future__ import annotations
from typing import List, Tuple, Dict, Any
import random
import time
import copy

from core.models import Package, Truck
from geneticAlgorithm.models import Gene, Individual

class GeneticAlgorithm:
    def __init__(self, packages: List[Package], truck: Truck, population_size=60,
                 generations=100, crossover_rate=0.85, mutation_rate=0.12,
                 elite_count=2, tournament_size=3, seed=None):
        if population_size < 2:
            raise ValueError("population_size harus >= 2")
        if generations < 1:
            raise ValueError("generations harus >= 1")
        self.packages = packages
        self.truck = truck
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_count = min(elite_count, population_size - 1)
        self.tournament_size = max(2, tournament_size)
        self.rng = random.Random(seed)
        self.best_history: List[float] = []
        self.avg_history: List[float] = []
        self.population_history: List[Dict[str, float]] = []
        self.initial_state = None
        self.final_state = None
        self.duration = 0.0

    def _random_gene(self, i: int) -> Gene:
        p = self.packages[i]
        ori = self.rng.randrange(len(p.orientations()))
        dims = p.orientations()[ori]
        fits = dims[0] <= self.truck.w and dims[1] <= self.truck.l and dims[2] <= self.truck.h
        inside = fits and self.rng.random() < 0.72
        if not inside:
            return Gene(False, -1, -1, -1, ori)
        return Gene(True,
                    self.rng.randint(0, self.truck.w - dims[0]),
                    self.rng.randint(0, self.truck.l - dims[1]),
                    self.rng.randint(0, self.truck.h - dims[2]), ori)

    def random_individual(self) -> Individual:
        ind = Individual([self._random_gene(i) for i in range(len(self.packages))])
        return self.repair(ind)

    def _dims(self, i: int, gene: Gene) -> Tuple[int, int, int]:
        orientations = self.packages[i].orientations()
        return orientations[gene.orientation % len(orientations)]

    @staticmethod
    def _overlap(a, b) -> bool:
        return (a[0] < b[0] + b[3] and a[0] + a[3] > b[0] and
                a[1] < b[1] + b[4] and a[1] + a[4] > b[1] and
                a[2] < b[2] + b[5] and a[2] + a[5] > b[2])

    def _box(self, i: int, g: Gene):
        w, l, h = self._dims(i, g)
        return (g.x, g.y, g.z, w, l, h)

    def _supported(self, i: int, g: Gene, placed: List[Tuple[int, Gene]]) -> bool:
        box = self._box(i, g)
        if box[2] == 0:
            return True
        supported_cells = set()
        for j, other_gene in placed:
            other = self._box(j, other_gene)
            if other[2] + other[5] != box[2]:
                continue
            if self.packages[j].fragile:
                continue  # fragile packages cannot serve as support
            x0 = max(box[0], other[0]); x1 = min(box[0] + box[3], other[0] + other[3])
            y0 = max(box[1], other[1]); y1 = min(box[1] + box[4], other[1] + other[4])
            for x in range(x0, x1):
                for y in range(y0, y1):
                    supported_cells.add((x, y))
        required = {(x, y) for x in range(box[0], box[0] + box[3])
                    for y in range(box[1], box[1] + box[4])}
        return required.issubset(supported_cells)

    def repair(self, individual: Individual) -> Individual:
        ind = copy.deepcopy(individual)
        for i, g in enumerate(ind.genes):
            g.orientation %= len(self.packages[i].orientations())
            if not g.inside:
                g.x = g.y = g.z = -1

        candidates = [i for i, g in enumerate(ind.genes) if g.inside]
        candidates.sort(key=lambda i: (ind.genes[i].z, -self.packages[i].value, i))
        placed: List[Tuple[int, Gene]] = []
        weight = 0.0
        accepted = []

        for i in candidates:
            p = self.packages[i]
            g = ind.genes[i]
            dims = self._dims(i, g)
            x, y, z = g.x, g.y, g.z
            w, l, h = dims
            in_bounds = (x >= 0 and y >= 0 and z >= 0 and
                         x + w <= self.truck.w and y + l <= self.truck.l and
                         z + h <= self.truck.h)
            if not in_bounds or weight + p.weight > self.truck.max_capacity:
                g.inside = False; g.x = g.y = g.z = -1
                continue

            box = self._box(i, g)
            if any(self._overlap(box, self._box(j, gj)) for j, gj in placed):
                g.inside = False; g.x = g.y = g.z = -1
                continue

            if z > 0 and not self._supported(i, g, placed):
                g.inside = False; g.x = g.y = g.z = -1
                continue
            if p.fragile and any(self._box(j, gj)[2] >= z + h for j, gj in placed):
                g.inside = False; g.x = g.y = g.z = -1
                continue

            placed.append((i, g))
            accepted.append(i)
            weight += p.weight

        for i, gi in list(placed):
            if self.packages[i].fragile:
                bi = self._box(i, gi)
                for j, gj in list(placed):
                    if i == j:
                        continue
                    bj = self._box(j, gj)
                    if bj[2] >= bi[2] + bi[5] and self._overlap(
                        (bi[0], bi[1], bi[2] + bi[5], bi[3], bi[4], 1),
                        (bj[0], bj[1], bj[2], bj[3], bj[4], bj[5])
                    ):
                        gj.inside = False; gj.x = gj.y = gj.z = -1

        loaded = [i for i, g in enumerate(ind.genes) if g.inside]
        ind.loaded_value = sum(self.packages[i].value for i in loaded)
        ind.loaded_weight = sum(self.packages[i].weight for i in loaded)
        ind.valid_count = len(loaded)
        ind.fitness = ind.loaded_value
        return ind

    def _select(self, population: List[Individual]) -> Individual:
        contenders = self.rng.sample(population, min(self.tournament_size, len(population)))
        return copy.deepcopy(max(contenders, key=lambda x: x.fitness))

    def _crossover(self, a: Individual, b: Individual):
        if self.rng.random() >= self.crossover_rate:
            return copy.deepcopy(a), copy.deepcopy(b)
        c1, c2 = copy.deepcopy(a), copy.deepcopy(b)
        for i in range(len(self.packages)):
            if self.rng.random() < 0.5:
                c1.genes[i], c2.genes[i] = copy.deepcopy(b.genes[i]), copy.deepcopy(a.genes[i])
        return self.repair(c1), self.repair(c2)

    def _mutate(self, individual: Individual) -> Individual:
        child = copy.deepcopy(individual)
        for i, g in enumerate(child.genes):
            if self.rng.random() >= self.mutation_rate:
                continue
            p = self.packages[i]
            action = self.rng.choice(("toggle", "move", "rotate"))
            if action == "toggle":
                g.inside = not g.inside
                if g.inside:
                    ori = g.orientation % len(p.orientations())
                    w, l, h = p.orientations()[ori]
                    if w <= self.truck.w and l <= self.truck.l and h <= self.truck.h:
                        g.x = self.rng.randint(0, self.truck.w - w)
                        g.y = self.rng.randint(0, self.truck.l - l)
                        g.z = self.rng.randint(0, self.truck.h - h)
                    else:
                        g.inside = False
                else:
                    g.x = g.y = g.z = -1
            elif action == "rotate":
                g.orientation = self.rng.randrange(len(p.orientations()))
                if g.inside:
                    w, l, h = p.orientations()[g.orientation]
                    if w <= self.truck.w and l <= self.truck.l and h <= self.truck.h:
                        g.x = min(max(g.x, 0), self.truck.w - w)
                        g.y = min(max(g.y, 0), self.truck.l - l)
                        g.z = min(max(g.z, 0), self.truck.h - h)
                    else:
                        g.inside = False; g.x = g.y = g.z = -1
            elif action == "move" and g.inside:
                w, l, h = p.orientations()[g.orientation]
                if w <= self.truck.w and l <= self.truck.l and h <= self.truck.h:
                    g.x = self.rng.randint(0, self.truck.w - w)
                    g.y = self.rng.randint(0, self.truck.l - l)
                    g.z = self.rng.randint(0, self.truck.h - h)
        return self.repair(child)

    def _snapshot(self, ind: Individual) -> Dict[str, Any]:
        packages = {}
        for i, p in enumerate(self.packages):
            g = ind.genes[i]
            packages[p.id] = {
                "inside": g.inside,
                "coordinate": [g.x, g.y, g.z] if g.inside else None,
                "orientation_dimensions": list(self._dims(i, g)),
                "value": p.value, "weight": p.weight, "fragile": p.fragile
            }
        return {"packages": packages, "objective_value": ind.loaded_value,
                "total_weight": ind.loaded_weight, "loaded_count": ind.valid_count}

    def run(self) -> Dict[str, Any]:
        start = time.perf_counter()
        population = [self.random_individual() for _ in range(self.population_size)]
        self.initial_state = self._snapshot(max(population, key=lambda x: x.fitness))
        for generation in range(self.generations + 1):
            fitnesses = [x.fitness for x in population]
            self.best_history.append(max(fitnesses))
            self.avg_history.append(sum(fitnesses) / len(fitnesses))
            self.population_history.append({"generation": generation,
                                            "max_fitness": max(fitnesses),
                                            "average_fitness": sum(fitnesses) / len(fitnesses)})
            if generation == self.generations:
                break
            population.sort(key=lambda x: x.fitness, reverse=True)
            next_population = [copy.deepcopy(x) for x in population[:self.elite_count]]
            while len(next_population) < self.population_size:
                p1, p2 = self._select(population), self._select(population)
                c1, c2 = self._crossover(p1, p2)
                next_population.append(self._mutate(c1))
                if len(next_population) < self.population_size:
                    next_population.append(self._mutate(c2))
            population = next_population

        best = max(population, key=lambda x: x.fitness)
        self.final_state = self._snapshot(best)
        self.duration = time.perf_counter() - start
        return {
            "initial_state": self.initial_state,
            "final_state": self.final_state,
            "best_history": self.best_history,
            "average_history": self.avg_history,
            "population_history": self.population_history,
            "duration_seconds": self.duration,
            "population_size": self.population_size,
            "generations": self.generations,
            "final_objective": best.fitness
        }
