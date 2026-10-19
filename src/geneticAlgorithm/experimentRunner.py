from pathlib import Path
import csv
import json
import time
import matplotlib.pyplot as plt

from geneticAlgorithm.geneticAlgorithm import GeneticAlgorithm
from geneticAlgorithm.models import Truck
from config import TRUCK_DIMENSIONS, TRUCK_MAX_CAPACITY, OUTPUT_DIR

def create_truck():
    w, l, h = TRUCK_DIMENSIONS
    return Truck(w=w, l=l, h=h, max_capacity=TRUCK_MAX_CAPACITY)

def run_one(packages, truck, population, generations, seed, label, output_dir=OUTPUT_DIR):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    ga = GeneticAlgorithm(packages, truck, population_size=population,
                          generations=generations, seed=seed)
    result = ga.run()
    prefix = f"{label}_pop{population}_gen{generations}_seed{seed}"

    (output / f"{prefix}_states.json").write_text(json.dumps({
        "initial_state": result["initial_state"],
        "final_state": result["final_state"]
    }, indent=2), encoding="utf-8")

    with (output / f"{prefix}_history.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["generation", "max_fitness", "average_fitness"])
        writer.writeheader()
        writer.writerows(result["population_history"])

    x = range(len(result["best_history"]))
    plt.figure()
    plt.plot(x, result["best_history"], color="#386641", label="Maksimum populasi")
    plt.plot(x, result["average_history"], color="#386641", linestyle="--",
             label="Rata-rata populasi")
    plt.xlabel("Generasi")
    plt.ylabel("Objective function (value)")
    plt.title(f"GA: populasi={population}, generasi={generations}, run={seed}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / f"{prefix}_fitness.png", dpi=150)
    plt.close()

    return {
        "experiment": label, "population_size": population, "generations": generations,
        "run": seed, "final_objective": result["final_objective"],
        "duration_seconds": result["duration_seconds"],
        "final_weight": result["final_state"]["total_weight"],
        "loaded_count": result["final_state"]["loaded_count"],
        "state_file": f"{prefix}_states.json",
        "history_file": f"{prefix}_history.csv",
        "plot_file": f"{prefix}_fitness.png"
    }

def save_summary(rows, output_dir=OUTPUT_DIR):
    if not rows:
        return
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def run_pilot(packages, truck, population, generations):
    start = time.perf_counter()
    result = run_one(packages, truck, population, generations, 1000, "pilot")
    return result, time.perf_counter() - start
