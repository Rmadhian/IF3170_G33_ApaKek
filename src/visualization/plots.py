import os
from typing import List, Optional
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# bikin folder kalau belum ada
def ensure_dir(filepath: str) -> None:
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)


# plot objektif per iterasi
def plot_objective_history(
    objective_history: List[float],
    algorithm_name: str,
    save_path: Optional[str] = None,
    best_history: Optional[List[float]] = None,
) -> go.Figure:
    iterations = list(range(len(objective_history)))

    # png buat laporan
    if save_path:
        ensure_dir(save_path)
        plt.figure(figsize=(10, 5))
        plt.plot(iterations, objective_history, label="Current Objective Value", color="#2563eb", alpha=0.8, linewidth=1.5)
        if best_history:
            plt.plot(iterations, best_history, label="Best Objective Value", color="#dc2626", linestyle="--", linewidth=1.8)
        plt.title(f"Nilai Objective Function terhadap Iterasi ({algorithm_name})")
        plt.xlabel("Iterasi")
        plt.ylabel("Nilai Objective Function")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    # versi interaktif buat demo
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=iterations,
            y=objective_history,
            mode="lines",
            name="Current Score",
            line=dict(color="#2563eb", width=2),
        )
    )
    if best_history:
        fig.add_trace(
            go.Scatter(
                x=iterations,
                y=best_history,
                mode="lines",
                name="Best Score",
                line=dict(color="#dc2626", width=2, dash="dash"),
            )
        )
    fig.update_layout(
        title=f"Objective Function vs Iterasi — {algorithm_name}",
        xaxis_title="Iterasi",
        yaxis_title="Nilai Objective Function",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


# plot e^(dE/T) SA
def plot_sa_acceptance_prob(
    acceptance_prob_history: List[float],
    temperature_history: Optional[List[float]] = None,
    stuck_iterations: Optional[List[int]] = None,
    save_path: Optional[str] = None,
) -> go.Figure:
    iterations = list(range(len(acceptance_prob_history)))

    # png buat laporan
    if save_path:
        ensure_dir(save_path)
        fig_mpl, ax1 = plt.subplots(figsize=(10, 5))
        ax1.scatter(
            iterations,
            acceptance_prob_history,
            s=6,
            alpha=0.45,
            color="#059669",
            label=r"Acceptance Probability ($e^{\Delta E / T}$)",
        )
        ax1.set_xlabel("Iterasi")
        ax1.set_ylabel(r"Probabilitas Penerimaan ($e^{\Delta E / T}$)", color="#059669")
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, linestyle="--", alpha=0.5)

        if stuck_iterations:
            stuck_probs = [acceptance_prob_history[i] for i in stuck_iterations if i < len(acceptance_prob_history)]
            ax1.scatter(
                stuck_iterations,
                stuck_probs,
                color="#dc2626",
                marker="x",
                s=45,
                zorder=5,
                label=f"Stuck Event (Total: {len(stuck_iterations)}x)",
            )

        if temperature_history:
            ax2 = ax1.twinx()
            ax2.plot(iterations, temperature_history, color="#d97706", linestyle="--", alpha=0.7, label="Temperatur (T)")
            ax2.set_ylabel("Temperatur (T)", color="#d97706")
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
        else:
            ax1.legend(loc="upper right")

        plt.title(r"Plot $e^{\Delta E / T}$ terhadap Iterasi (Simulated Annealing)")
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    # versi interaktif buat demo
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scattergl(
            x=iterations,
            y=acceptance_prob_history,
            mode="markers",
            name="e^(ΔE/T)",
            marker=dict(size=4, color="#059669", opacity=0.5),
        ),
        secondary_y=False,
    )

    if stuck_iterations:
        stuck_probs = [acceptance_prob_history[i] for i in stuck_iterations if i < len(acceptance_prob_history)]
        fig.add_trace(
            go.Scatter(
                x=stuck_iterations,
                y=stuck_probs,
                mode="markers",
                name=f"Stuck ({len(stuck_iterations)}x)",
                marker=dict(size=9, color="#dc2626", symbol="x"),
            ),
            secondary_y=False,
        )

    if temperature_history:
        fig.add_trace(
            go.Scatter(
                x=iterations,
                y=temperature_history,
                mode="lines",
                name="Temperatur (T)",
                line=dict(color="#d97706", width=2, dash="dot"),
            ),
            secondary_y=True,
        )
        fig.update_yaxes(title_text="Temperatur (T)", secondary_y=True)

    fig.update_layout(
        title="Simulated Annealing: Probabilitas Penerimaan e^(ΔE/T) vs Iterasi",
        xaxis_title="Iterasi",
        template="plotly_white",
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Acceptance Probability e^(ΔE/T)", range=[-0.05, 1.05], secondary_y=False)
    return fig


# plot max dan rata-rata populasi GA
def plot_ga_population_history(
    max_fitness_history: List[float],
    avg_fitness_history: List[float],
    pop_size: int,
    max_generations: int,
    save_path: Optional[str] = None,
) -> go.Figure:
    generations = list(range(len(max_fitness_history)))
    subtitle = f"(Populasi = {pop_size}, Iterasi = {max_generations})"

    # png buat laporan
    if save_path:
        ensure_dir(save_path)
        plt.figure(figsize=(10, 5))
        plt.plot(generations, max_fitness_history, label="Max Objective Populasi", color="#16a34a", linewidth=2)
        plt.plot(generations, avg_fitness_history, label="Rata-rata Objective Populasi", color="#2563eb", linestyle="--", linewidth=1.8)
        plt.title(f"Genetic Algorithm: Max & Rata-rata Objective vs Iterasi\n{subtitle}")
        plt.xlabel("Generasi / Iterasi")
        plt.ylabel("Nilai Objective Function")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    # versi interaktif buat demo
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=max_fitness_history,
            mode="lines",
            name="Max Populasi",
            line=dict(color="#16a34a", width=2.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=avg_fitness_history,
            mode="lines",
            name="Rata-rata Populasi",
            line=dict(color="#2563eb", width=2, dash="dash"),
        )
    )
    fig.update_layout(
        title=f"Genetic Algorithm: Max & Rata-rata Populasi vs Iterasi {subtitle}",
        xaxis_title="Iterasi / Generasi",
        yaxis_title="Nilai Objective Function",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig