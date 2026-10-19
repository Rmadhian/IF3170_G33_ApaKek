import random
import time

from core.models import random_state
from core.neighbors import all_neighbors
from core.objective import objective


# steepest ascent hill climbing
def steepest_ascent(packages, truck, initial=None, seed=None):
    rng = random.Random(seed)
    start = time.perf_counter()
    current = initial.copy() if initial else random_state(packages, truck, rng)
    initial_state = current.copy()
    current_value = objective(current, packages, truck)
    history = [current_value]

    while True:
        best, best_value = None, current_value
        for neighbor in all_neighbors(current, packages, truck):
            value = objective(neighbor, packages, truck)
            if value > best_value:
                best, best_value = neighbor, value
        if best is None:
            break
        current, current_value = best, best_value
        history.append(current_value)

    return {
        "initial_state": initial_state,
        "final_state": current,
        "final_objective": current_value,
        "history": history,
        "iterations": len(history) - 1,
        "duration": time.perf_counter() - start,
    }
