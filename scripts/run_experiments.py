"""Quick smoke-run: compare naive vs greedy across several scenarios."""
import json
from pathlib import Path

from app.algorithms.greedy import solve_greedy
from app.algorithms.naive import solve_naive
from app.core.metrics import compute_metrics
from app.core.models import ConstraintConfig
from app.services.scenario_generator import generate_scenario

CONSTRAINTS = ConstraintConfig(max_distance=500.0, max_route_time=500.0, capacity=999)
OUT_DIR = Path("results")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_experiment(num_orders: int, seed: int) -> dict:
    scenario = generate_scenario(num_orders=num_orders, seed=seed)
    total = len(scenario.orders)

    naive_route = solve_naive(scenario, CONSTRAINTS)
    greedy_route = solve_greedy(scenario, CONSTRAINTS)

    return {
        "num_orders": num_orders,
        "seed": seed,
        "naive": compute_metrics(naive_route, total),
        "greedy": compute_metrics(greedy_route, total),
    }


def main():
    results = []
    for n in [10, 20, 40]:
        for seed in [42, 7, 99]:
            r = run_experiment(n, seed)
            results.append(r)
            print(f"n={n} seed={seed} | naive_dist={r['naive']['total_distance']:.1f} greedy_dist={r['greedy']['total_distance']:.1f}")

    out = OUT_DIR / "baseline_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved results to {out}")


if __name__ == "__main__":
    main()
