from __future__ import annotations
from dataclasses import dataclass
from typing import List


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