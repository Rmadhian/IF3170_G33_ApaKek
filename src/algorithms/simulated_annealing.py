import math
import random
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SAResult:
    """Struktur data penyimpan hasil run Simulated Annealing untuk eksperimen & visualisasi."""
    initial_state: Any
    final_state: Any
    best_state: Any
    initial_score: float
    final_score: float
    best_score: float
    iterations: int
    duration_sec: float
    stuck_count: int
    stuck_events_iterations: List[int] = field(default_factory=list)
    objective_history: List[float] = field(default_factory=list)
    best_objective_history: List[float] = field(default_factory=list)
    acceptance_prob_history: List[float] = field(default_factory=list)
    temperature_history: List[float] = field(default_factory=list)


class SimulatedAnnealing:
    """
    Implementasi algoritma Simulated Annealing untuk optimasi penempatan paket
    di dalam peti kemas truk (Mejiro Express).
    """

    def __init__(
        self,
        objective_fn: Callable[[Any], float],
        neighbor_fn: Callable[[Any], Any],
        initial_temp: float = 1000.0,
        cooling_rate: float = 0.995,
        min_temp: float = 1e-3,
        max_iterations: int = 5000,
        schedule_type: str = "geometric",  # Pilihan: "geometric", "linear", "logarithmic"
        stuck_window: int = 50,
        seed: Optional[int] = None,
    ):
        self.objective_fn = objective_fn
        self.neighbor_fn = neighbor_fn
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations
        self.schedule_type = schedule_type
        self.stuck_window = stuck_window
        self.seed = seed

    def _calculate_temperature(self, iteration: int, current_temp: float) -> float:
        """Menghitung temperatur T pada iterasi ke-t sesuai cooling schedule."""
        if self.schedule_type == "geometric":
            return current_temp * self.cooling_rate
        elif self.schedule_type == "linear":
            decrement = (self.initial_temp - self.min_temp) / max(1, self.max_iterations)
            return max(self.min_temp, self.initial_temp - iteration * decrement)
        elif self.schedule_type == "logarithmic":
            return self.initial_temp / math.log(iteration + 2)
        else:
            raise ValueError(f"Cooling schedule tidak dikenali: {self.schedule_type}")

    def run(self, initial_state: Any) -> SAResult:
        """
        Menjalankan pencarian Simulated Annealing dari initial_state.
        Tujuan: Memaksimalkan nilai objective function (E).
        """
        if self.seed is not None:
            random.seed(self.seed)

        start_time = time.perf_counter()

        current_state = deepcopy(initial_state)
        current_score = self.objective_fn(current_state)

        best_state = deepcopy(current_state)
        best_score = current_score

        initial_state_copy = deepcopy(current_state)
        initial_score = current_score

        temp = self.initial_temp

        objective_history: List[float] = [current_score]
        best_objective_history: List[float] = [best_score]
        acceptance_prob_history: List[float] = [1.0]
        temperature_history: List[float] = [temp]

        # Pelacak kondisi "stuck" di local optima
        stuck_count = 0
        stuck_events_iterations: List[int] = []
        no_improvement_streak = 0

        iteration = 0
        while iteration < self.max_iterations and temp > self.min_temp:
            iteration += 1

            # Bangkitkan 1 random successor/neighbor (mengizinkan swap, move, atau rotasi 90 derajat)
            candidate_state = self.neighbor_fn(current_state)
            candidate_score = self.objective_fn(candidate_state)

            # Karena maksimasi: delta_E = E(next) - E(current)
            delta_e = candidate_score - current_score

            if delta_e > 0:
                # Neighbor lebih baik -> langsung terima (probabilitas = 1.0)
                acceptance_prob = 1.0
                accepted = True
            else:
                # Neighbor lebih buruk atau sama -> terima dengan probabilitas e^(delta_E / T)
                acceptance_prob = math.exp(delta_e / temp) if temp > 0 else 0.0
                accepted = random.random() < acceptance_prob

            if accepted:
                current_state = candidate_state
                current_score = candidate_score

            # Perbarui best state global dan cek apakah terjebak (stagnan) di local optima
            if current_score > best_score:
                best_score = current_score
                best_state = deepcopy(current_state)
                no_improvement_streak = 0
            else:
                no_improvement_streak += 1
                # Jika selama `stuck_window` iterasi berturut-turut tidak ada perbaikan nilai objektif
                if no_improvement_streak >= self.stuck_window:
                    stuck_count += 1
                    stuck_events_iterations.append(iteration)
                    no_improvement_streak = 0  # Reset window untuk menghitung episode stuck berikutnya

            # Catat metrik iterasi
            objective_history.append(current_score)
            best_objective_history.append(best_score)
            acceptance_prob_history.append(acceptance_prob)
            temperature_history.append(temp)

            # Update temperatur sesuai cooling schedule
            temp = self._calculate_temperature(iteration, temp)

        duration_sec = time.perf_counter() - start_time

        return SAResult(
            initial_state=initial_state_copy,
            final_state=current_state,
            best_state=best_state,
            initial_score=initial_score,
            final_score=current_score,
            best_score=best_score,
            iterations=iteration,
            duration_sec=duration_sec,
            stuck_count=stuck_count,
            stuck_events_iterations=stuck_events_iterations,
            objective_history=objective_history,
            best_objective_history=best_objective_history,
            acceptance_prob_history=acceptance_prob_history,
            temperature_history=temperature_history,
        )