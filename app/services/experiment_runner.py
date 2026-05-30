"""Run all three algorithms across a grid of (num_orders, seed) combinations
and return results as a pandas DataFrame."""
from __future__ import annotations

import time
from typing import List

import pandas as pd

from app.algorithms.greedy import solve_greedy
from app.algorithms.naive import solve_naive
from app.algorithms.simulated_annealing import solve_sa
from app.core.metrics import compute_metrics
from app.core.models import ConstraintConfig, SAConfig
from app.services.scenario_generator import generate_scenario

DEFAULT_ORDERS = [10, 20, 40]
DEFAULT_SEEDS = [42, 7, 99]
DEFAULT_CONSTRAINTS = ConstraintConfig(
    max_distance=500.0,
    max_route_time=500.0,
    capacity=999,
)
DEFAULT_SA_CONFIG = SAConfig(
    initial_temp=1000.0,
    cooling_rate=0.995,
    min_temp=1.0,
    max_iterations=5000,
)


def run_experiments(
    orders_list: List[int] = DEFAULT_ORDERS,
    seeds: List[int] = DEFAULT_SEEDS,
    constraints: ConstraintConfig = DEFAULT_CONSTRAINTS,
    sa_config: SAConfig = DEFAULT_SA_CONFIG,
) -> pd.DataFrame:
    rows = []

    for n in orders_list:
        for seed in seeds:
            scenario = generate_scenario(num_orders=n, seed=seed)
            total = len(scenario.orders)

            for algo_name, solver_fn in [
                ("naive", lambda s: solve_naive(s, constraints)),
                ("greedy", lambda s: solve_greedy(s, constraints)),
                ("sa", lambda s: solve_sa(s, constraints, sa_config)),
            ]:
                t0 = time.perf_counter()
                route = solver_fn(scenario)
                elapsed = time.perf_counter() - t0

                metrics = compute_metrics(route, total)
                rows.append({
                    "num_orders": n,
                    "seed": seed,
                    "algorithm": algo_name,
                    "total_distance": metrics["total_distance"],
                    "total_time": metrics["total_time"],
                    "served_orders": metrics["served_orders"],
                    "service_rate": metrics["service_rate"],
                    "feasible": metrics["feasible"],
                    "runtime_ms": round(elapsed * 1000, 3),
                })

    return pd.DataFrame(rows)
