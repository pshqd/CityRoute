"""Generate experiment result plots and save them to results/."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

OUT_DIR = Path("results")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALGO_COLORS = {"naive": "#e07b39", "greedy": "#3a7abf", "sa": "#4caf7d"}


def _grouped_bar(
    df: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    filename: str,
) -> None:
    pivot = df.groupby(["num_orders", "algorithm"])[metric].mean().unstack()
    colors = [ALGO_COLORS.get(c, "#888") for c in pivot.columns]
    ax = pivot.plot(
        kind="bar",
        figsize=(9, 5),
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_title(title, fontsize=13, pad=12)
    ax.set_xlabel("Number of orders", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xticklabels(pivot.index.astype(str), rotation=0)
    ax.legend(title="Algorithm", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(OUT_DIR / filename, dpi=150)
    plt.close()


def plot_all(df: pd.DataFrame) -> None:
    _grouped_bar(
        df, "total_distance", "Avg total distance",
        "Total distance by algorithm", "distance_by_algorithm.png",
    )
    _grouped_bar(
        df, "service_rate", "Avg service rate",
        "Service rate by algorithm", "service_rate_by_algorithm.png",
    )
    _grouped_bar(
        df, "runtime_ms", "Avg runtime (ms)",
        "Runtime by algorithm", "runtime_by_algorithm.png",
    )
    print(f"Plots saved to {OUT_DIR}/")
