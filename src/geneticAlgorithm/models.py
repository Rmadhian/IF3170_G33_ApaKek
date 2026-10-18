from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


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


@dataclass(frozen=True)
class Truck:
    w: int
    l: int
    h: int
    max_capacity: float


@dataclass
class Gene:
    inside: bool
    x: int
    y: int
    z: int
    orientation: int


@dataclass
class Individual:
    genes: List[Gene]
    fitness: float = 0.0
    loaded_value: float = 0.0
    loaded_weight: float = 0.0
    valid_count: int = 0