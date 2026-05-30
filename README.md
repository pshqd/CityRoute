# CityRoute — Vehicle Routing Lite

Research backend for single-courier constrained routing.
Compares **naive baseline**, **greedy nearest-neighbour**, and **simulated annealing**.

## Stack

- Python 3.11 · uv
- FastAPI + Pydantic v2
- NumPy · pandas · NetworkX · SciPy
- matplotlib · plotly
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

# Run full experiment grid + save CSV + plots
uv run python scripts/run_experiments.py
```

## Project Structure

```
app/
  core/           # models, constraints, metrics
  algorithms/     # naive, greedy, simulated_annealing
  services/       # scenario_generator, graph_builder,
  |               # experiment_runner, plotter
  api/            # FastAPI routes
data/scenarios/   # generated JSON scenarios
results/          # CSV results + PNG plots
scripts/          # CLI helpers
tests/            # pytest suites
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/generate-scenario` | Generate synthetic scenario |
| POST | `/api/v1/solve` | Solve with naive / greedy / sa |
| POST | `/api/v1/compare` | Compare all three algorithms |

## Algorithms

| Algorithm | Strategy | Constraints |
|-----------|----------|-------------|
| Naive | Visit orders as-is, return to depot | Checked post-hoc |
| Greedy | Nearest-neighbour with lookahead | Respected during construction |
| Simulated Annealing | Greedy warm-start + swap/insert/reverse operators | Penalised in objective |

### SA Objective

```
score = total_distance
      + skipped_orders  × 500
      + constraint_violations × 1000
```

## Problem Statement

Single courier, one depot, N orders with locations and service times.
Goal: maximise orders served within `max_distance` and `max_route_time` constraints.

## Roadmap

- [x] Stage 1 — core models, naive & greedy solvers, API, tests
- [x] Stage 2 — simulated annealing, experiment runner, CSV + plots
- [ ] Stage 3 — Docker, GitHub Actions CI, Dockerfile polish
