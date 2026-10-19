import random
import time

from core.models import random_state
from core.neighbors import all_neighbors
from core.objective import objective


# tetangga terbaik, seri dipilih acak
def _best_neighbor(current, packages, truck, rng):
    best_value, best = None, []
    for neighbor in all_neighbors(current, packages, truck):
        value = objective(neighbor, packages, truck)
        if best_value is None or value > best_value:
            best_value, best = value, [neighbor]
        elif value == best_value:
            best.append(neighbor)
    return (rng.choice(best), best_value) if best else (None, None)


# hill climbing dengan batas total sideways
def _climb(packages, truck, initial, seed, max_sideways):
    rng = random.Random(seed)
    start = time.perf_counter()
    current = initial.copy() if initial else random_state(packages, truck, rng)
    initial_state = current.copy()
    current_value = objective(current, packages, truck)
    history = [current_value]
    sideways = 0

    while True:
        best, best_value = _best_neighbor(current, packages, truck, rng)
        if best is None or best_value < current_value:
            break
        if best_value == current_value:
            if sideways >= max_sideways:
                break
            sideways += 1
        current, current_value = best, best_value
        history.append(current_value)

    return {
        "initial_state": initial_state,
        "final_state": current,
        "final_objective": current_value,
        "history": history,
        "iterations": len(history) - 1,
        "sideways_moves": sideways,
        "duration": time.perf_counter() - start,
    }


# steepest ascent hill climbing
def steepest_ascent(packages, truck, initial=None, seed=None):
    return _climb(packages, truck, initial, seed, max_sideways=0)


# hill climbing with sideways move
def sideways_move(packages, truck, max_sideways=100, initial=None, seed=None):
    return _climb(packages, truck, initial, seed, max_sideways)
