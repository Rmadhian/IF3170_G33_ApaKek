import csv
import json
import sys
from pathlib import Path

from core.io import load_input, snapshot
from geneticAlgorithm.config import (
    FIXED_GENERATIONS, FIXED_POPULATION_SIZE, GENERATION_VARIANTS,
    POPULATION_VARIANTS, REPEATS,
)
from geneticAlgorithm.geneticAlgorithm import GeneticAlgorithm
from hillClimbing.hillClimbing import random_restart, sideways_move, steepest_ascent, stochastic
from simulatedAnnealing.simulatedAnnealing import run_sa
from visualization.plots import plot_ga_population_history, plot_objective_history, plot_sa_acceptance_prob
from visualization.viz_3d import visualize_container_state

ROOT = Path(__file__).resolve().parent.parent

HC_VARIANTS = {
    "steepest": (steepest_ascent, {}),
    "sideways": (sideways_move, {"max_sideways": 100}),
    "stochastic": (stochastic, {"max_iter": 1000}),
    "random_restart": (random_restart, {"max_restart": 10}),
}


# simpan state awal dan akhir ke json dan html 3d
def save_states(out, name, truck, initial, final, initial_score, final_score):
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}_states.json").write_text(json.dumps(
        {"initial_state": initial, "final_state": final}, indent=2), encoding="utf-8")
    for label, rows, score in (("awal", initial, initial_score), ("akhir", final, final_score)):
        fig = visualize_container_state((truck.w, truck.l, truck.h), truck.max_capacity,
            rows, score, title=f"{name} - state {label}")
        fig.write_html(out / f"{name}_{label}.html", include_plotlyjs="cdn")


# state GA ke format snapshot
def ga_rows(ga_state, packages):
    rows = []
    for pkg in packages:
        g = ga_state["packages"][pkg.id]
        x, y, z = g["coordinate"] if g["inside"] else (None, None, None)
        w, l, h = g["orientation_dimensions"]
        rows.append({"id": pkg.id, "in_truck": g["inside"], "x": x, "y": y, "z": z,
            "w": w, "l": l, "h": h, "value": pkg.value, "weight": pkg.weight,
            "is_fragile": pkg.fragile, "eta": pkg.eta})
    return rows


# semua varian HC, masing-masing 3 kali
def run_hc(packages, truck, out):
    rows = []
    for variant, (fn, params) in HC_VARIANTS.items():
        for run in range(1, REPEATS + 1):
            r = fn(packages, truck, seed=run, **params)
            name = f"hc_{variant}_run{run}"
            save_states(out, name, truck, snapshot(r["initial_state"], packages),
                snapshot(r["final_state"], packages), r["history"][0], r["final_objective"])
            plot_objective_history(r["history"], f"HC {variant} run {run}",
                save_path=str(out / f"{name}_objective.png"))
            extra = {k: r[k] for k in ("sideways_moves", "restarts", "iterations_per_restart") if k in r}
            rows.append({"algorithm": "HC", "variant": variant, "run": run, **params,
                "final_objective": r["final_objective"], "iterations": r["iterations"],
                "duration": round(r["duration"], 4), **extra})
            print(name, r["final_objective"], f"{r['duration']:.2f}s")
    return rows


# SA 3 kali
def run_sa_all(packages, truck, out):
    rows = []
    for run in range(1, REPEATS + 1):
        r = run_sa(packages, truck, seed=run)
        name = f"sa_run{run}"
        save_states(out, name, truck, snapshot(r.initial_state, packages),
            snapshot(r.best_state, packages), r.initial_score, r.best_score)
        plot_objective_history(r.objective_history, f"SA run {run}",
            save_path=str(out / f"{name}_objective.png"), best_history=r.best_objective_history)
        plot_sa_acceptance_prob(r.acceptance_prob_history, r.temperature_history,
            r.stuck_events_iterations, save_path=str(out / f"{name}_acceptance.png"))
        rows.append({"algorithm": "SA", "variant": "geometric", "run": run,
            "final_objective": r.best_score, "iterations": r.iterations,
            "duration": round(r.duration_sec, 4), "stuck_count": r.stuck_count})
        print(name, r.best_score, f"{r.duration_sec:.2f}s")
    return rows


# GA, populasi dan iterasi bergantian jadi kontrol
def run_ga_all(packages, truck, out):
    configs = [("kontrol_populasi", FIXED_POPULATION_SIZE, g) for g in GENERATION_VARIANTS]
    configs += [("kontrol_iterasi", p, FIXED_GENERATIONS) for p in POPULATION_VARIANTS]
    rows = []
    for label, pop, gen in configs:
        for run in range(1, REPEATS + 1):
            r = GeneticAlgorithm(packages, truck, population_size=pop,
                generations=gen, seed=run).run()
            name = f"ga_{label}_pop{pop}_gen{gen}_run{run}"
            save_states(out, name, truck, ga_rows(r["initial_state"], packages),
                ga_rows(r["final_state"], packages),
                r["initial_state"]["objective_value"], r["final_objective"])
            plot_ga_population_history(r["best_history"], r["average_history"], pop, gen,
                save_path=str(out / f"{name}_fitness.png"))
            rows.append({"algorithm": "GA", "variant": label, "run": run,
                "population": pop, "generations": gen, "final_objective": r["final_objective"],
                "iterations": gen, "duration": round(r["duration_seconds"], 4)})
            print(name, r["final_objective"], f"{r['duration_seconds']:.2f}s")
    return rows


# tulis ringkasan semua run
def save_summary(rows, path):
    fields = []
    for row in rows:
        fields += [k for k in row if k not in fields]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "input" / "contoh.json"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "output"
    packages, truck = load_input(input_path)

    rows = run_hc(packages, truck, out / "hc")
    rows += run_sa_all(packages, truck, out / "sa")
    rows += run_ga_all(packages, truck, out / "ga")
    save_summary(rows, out / "summary.csv")
    print(f"selesai, ringkasan di {out / 'summary.csv'}")


if __name__ == "__main__":
    main()
