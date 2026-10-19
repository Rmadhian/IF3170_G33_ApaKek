import os
from typing import Any, Tuple
from src.algorithms.simulated_annealing import SAResult
from src.visualization.viz_3d import visualize_container_state
from src.visualization.plots import plot_objective_history, plot_sa_acceptance_prob


def export_sa_demo_report(
    sa_result: SAResult,
    truck_dims: Tuple[int, int, int],
    max_capacity: float,
    packages_initial: list,
    packages_final: list,
    output_dir: str = "output/sa_demo",
    run_id: int = 1,
) -> str:
    """
    Menghasilkan halaman dashboard HTML interaktif untuk demo serta menyimpan plot PNG untuk laporan.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Hasilkan Figure 3D Initial & Final State
    fig_init = visualize_container_state(
        truck_dims=truck_dims,
        max_capacity=max_capacity,
        packages=packages_initial,
        state_score=sa_result.initial_score,
        title=f"SA Run #{run_id} — Initial State",
    )
    fig_final = visualize_container_state(
        truck_dims=truck_dims,
        max_capacity=max_capacity,
        packages=packages_final,
        state_score=sa_result.best_score,
        title=f"SA Run #{run_id} — Final State (Durasi: {sa_result.duration_sec:.3f}s | Stuck: {sa_result.stuck_count}x)",
    )

    # Hasilkan Plot Eksperimen (simpan PNG sekaligus ambil objek Plotly)
    fig_obj = plot_objective_history(
        objective_history=sa_result.objective_history,
        best_history=sa_result.best_objective_history,
        algorithm_name=f"Simulated Annealing (Run #{run_id})",
        save_path=os.path.join(output_dir, f"sa_run_{run_id}_objective.png"),
    )
    fig_prob = plot_sa_acceptance_prob(
        acceptance_prob_history=sa_result.acceptance_prob_history,
        temperature_history=sa_result.temperature_history,
        stuck_iterations=sa_result.stuck_events_iterations,
        save_path=os.path.join(output_dir, f"sa_run_{run_id}_acceptance_prob.png"),
    )

    # Gabungkan menjadi satu file HTML interaktif untuk Demo
    dashboard_path = os.path.join(output_dir, f"sa_demo_run_{run_id}.html")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Demo Tugas Besar 1 IF3170 - Mejiro Express</title>")
        f.write("<style>body{font-family:sans-serif; margin:24px; background:#f1f5f9;} .card{background:white; padding:16px; margin-bottom:24px; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,0.08);}</style></head><body>")
        f.write(f"<h1>Demo Simulated Annealing — Mejiro Express (Run #{run_id})</h1>")
        f.write(
            f"<div class='card'><h3>Ringkasan Eksperimen</h3>"
            f"<p><b>Initial Objective Score:</b> {sa_result.initial_score:.2f} | "
            f"<b>Final Best Score:</b> {sa_result.best_score:.2f} | "
            f"<b>Total Iterasi:</b> {sa_result.iterations} | "
            f"<b>Durasi:</b> {sa_result.duration_sec:.4f} detik | "
            f"<b>Frekuensi Stuck di Local Optima:</b> {sa_result.stuck_count} kali</p></div>"
        )
        f.write("<div class='card'>" + fig_init.to_html(full_html=False, include_plotlyjs="cdn") + "</div>")
        f.write("<div class='card'>" + fig_final.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("<div class='card'>" + fig_obj.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("<div class='card'>" + fig_prob.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("</body></html>")

    return dashboard_path