import random
from typing import Iterator, List, Tuple

from core.models import Package, State, Truck

# sumbu rotasi -> pasangan dimensi yang ditukar
AXIS_SWAP = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}


# tukar posisi dua paket
def swap(state: State, i: int, j: int) -> State:
    new = state.copy()
    a, b = new.placements[i], new.placements[j]
    a.inside, b.inside = b.inside, a.inside
    a.x, b.x = b.x, a.x
    a.y, b.y = b.y, a.y
    a.z, b.z = b.z, a.z
    return new


# pindahkan paket ke koordinat lain
def move(state: State, i: int, pos) -> State:
    new = state.copy()
    p = new.placements[i]
    if pos is None:
        p.inside, p.x, p.y, p.z = False, -1, -1, -1
    else:
        p.inside, (p.x, p.y, p.z) = True, pos
    return new


# rotasi 90 derajat terhadap satu sumbu
def rotate(state: State, i: int, axis: str, packages: List[Package]) -> State:
    dims = list(state.dims(i, packages))
    a, b = AXIS_SWAP[axis]
    dims[a], dims[b] = dims[b], dims[a]
    new = state.copy()
    new.placements[i].orientation = packages[i].orientations().index(tuple(dims))
    return new


# kandidat posisi: pojok truk dan sisi paket lain
def candidate_positions(state: State, i: int, packages: List[Package],
    truck: Truck) -> List[Tuple[int, int, int]]:
    w, l, h = state.dims(i, packages)
    spots = {(0, 0, 0)}
    for j in state.inside_indices():
        if j == i:
            continue
        x, y, z, bw, bl, bh = state.box(j, packages)
        spots.update({(x + bw, y, z), (x, y + bl, z), (x, y, z + bh)})
    p = state.placements[i]
    if p.inside:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            spots.add((p.x + dx, p.y + dy, p.z + dz))
        spots.discard((p.x, p.y, p.z))
    return sorted(s for s in spots
        if 0 <= s[0] <= truck.w - w and 0 <= s[1] <= truck.l - l
        and 0 <= s[2] <= truck.h - h)


# semua tetangga dari satu state
def all_neighbors(state: State, packages: List[Package], truck: Truck) -> Iterator[State]:
    n = len(packages)
    for i in range(n):
        for j in range(i + 1, n):
            if state.placements[i].inside or state.placements[j].inside:
                yield swap(state, i, j)
    for i in range(n):
        for pos in candidate_positions(state, i, packages, truck):
            yield move(state, i, pos)
        if state.placements[i].inside:
            yield move(state, i, None)
    for i in range(n):
        for axis in AXIS_SWAP:
            new = rotate(state, i, axis, packages)
            if new.placements[i].orientation != state.placements[i].orientation:
                yield new


# satu tetangga acak
def random_neighbor(state: State, packages: List[Package], truck: Truck,
        rng: random.Random) -> State:
    n = len(packages)
    action = rng.choice(("swap", "move", "rotate"))
    if action == "swap" and n > 1:
        i, j = rng.sample(range(n), 2)
        return swap(state, i, j)
    i = rng.randrange(n)
    if action == "rotate":
        return rotate(state, i, rng.choice(tuple(AXIS_SWAP)), packages)
    spots = candidate_positions(state, i, packages, truck)
    if state.placements[i].inside and (not spots or rng.random() < 0.1):
        return move(state, i, None)
    return move(state, i, rng.choice(spots)) if spots else state.copy()
