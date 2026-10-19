from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Tuple


# data paket, sama dengan model GA
@dataclass(frozen=True)
class Package:
    id: str
    w: int
    l: int
    h: int
    value: float
    weight: float
    fragile: bool = False
    eta: int = 0

    def orientations(self) -> List[Tuple[int, int, int]]:
        return list(dict.fromkeys([
            (self.w, self.l, self.h), (self.w, self.h, self.l),
            (self.l, self.w, self.h), (self.l, self.h, self.w),
            (self.h, self.w, self.l), (self.h, self.l, self.w)
        ]))


# data truk, sama dengan model GA
@dataclass(frozen=True)
class Truck:
    w: int
    l: int
    h: int
    max_capacity: float


# posisi dan orientasi satu paket
@dataclass
class Placement:
    inside: bool
    x: int = -1
    y: int = -1
    z: int = -1
    orientation: int = 0


# satu state = placement untuk tiap paket
@dataclass
class State:
    placements: List[Placement] = field(default_factory=list)

    def copy(self) -> State:
        return State([Placement(p.inside, p.x, p.y, p.z, p.orientation)
            for p in self.placements])

    def dims(self, i: int, packages: List[Package]) -> Tuple[int, int, int]:
        ori = packages[i].orientations()
        return ori[self.placements[i].orientation % len(ori)]

    def box(self, i: int, packages: List[Package]) -> Tuple[int, int, int, int, int, int]:
        p = self.placements[i]
        w, l, h = self.dims(i, packages)
        return (p.x, p.y, p.z, w, l, h)

    def inside_indices(self) -> List[int]:
        return [i for i, p in enumerate(self.placements) if p.inside]


# state awal acak
def random_state(packages: List[Package], truck: Truck, rng: random.Random) -> State:
    placements = []
    for pkg in packages:
        ori = rng.randrange(len(pkg.orientations()))
        w, l, h = pkg.orientations()[ori]
        fits = w <= truck.w and l <= truck.l and h <= truck.h
        if fits and rng.random() < 0.5:
            placements.append(Placement(True, rng.randint(0, truck.w - w),
                rng.randint(0, truck.l - l), rng.randint(0, truck.h - h), ori))
        else:
            placements.append(Placement(False, orientation=ori))
    return State(placements)
