# CityRoute — Vehicle Routing Lite

Research backend for single-courier constrained routing.
Compares **naive baseline**, **greedy nearest-neighbour**, and (soon) **simulated annealing**.

## Stack

- Python 3.11 · uv
- FastAPI + Pydantic v2
- NumPy · pandas · NetworkX · SciPy
- pytest · ruff

## Quickstart

```bash
# Install dependencies
uv sync --all-extras

# Run API
uv run uvicorn app.main:app --reload
# → http://127.0.0.1:8000/docs

# Run tests
uv run pytest

# Generate scenarios
uv run python scripts/generate_scenarios.py

# Smoke-run experiments
uv run python scripts/run_experiments.py
```

## Project Structure

```
app/
  core/        # models, constraints, metrics
  algorithms/  # naive, greedy, (simulated_annealing)
  services/    # scenario_generator, graph_builder
  api/         # FastAPI routes
data/scenarios/  # generated JSON scenarios
results/         # experiment outputs
scripts/         # CLI helpers
tests/           # pytest suites
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/generate-scenario` | Generate synthetic scenario |
| POST | `/api/v1/solve` | Solve with one algorithm |
| POST | `/api/v1/compare` | Compare naive vs greedy |

## Problem Statement

Single courier, one depot, N orders with locations and service times.
Goal: maximize orders served within `max_distance` and `max_route_time` constraints.

## Roadmap

- [x] Stage 1 — core models, naive & greedy solvers, API, tests
- [ ] Stage 2 — simulated annealing, experiment runner with CSV output, plots
- [ ] Stage 3 — Docker, full README, GitHub Actions CI
