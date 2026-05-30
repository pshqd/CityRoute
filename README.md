# CityRoute — Vehicle Routing Lite

[![CI](https://github.com/pshqd/CityRoute/actions/workflows/ci.yml/badge.svg)](https://github.com/pshqd/CityRoute/actions/workflows/ci.yml)

Research backend for **single-courier constrained routing**.
Compares three algorithms — naive baseline, greedy nearest-neighbour,
and simulated annealing — on synthetic 2-D scenarios with configurable
distance and time constraints.

---

## Stack

| Layer | Tools |
|---|---|
| Language | Python 3.12 · uv |
| API | FastAPI · Pydantic v2 |
| Numerics | NumPy · SciPy · NetworkX |
| Analysis | pandas · matplotlib · plotly |
| Quality | pytest · pytest-cov · ruff |
| Infra | Docker · GitHub Actions |

---

## Quickstart

```bash
git clone https://github.com/pshqd/CityRoute.git
cd CityRoute
uv sync --all-extras

uv run uvicorn app.main:app --reload
# → http://127.0.0.1:8000/docs

uv run pytest -v
```

### Docker

```bash
docker compose up --build
# → http://localhost:8000/docs
```

---

## Project Structure

```
CityRoute/
├── app/
│   ├── core/
│   │   ├── models.py
│   │   ├── constraints.py
│   │   └── metrics.py
│   ├── algorithms/
│   │   ├── naive.py
│   │   ├── greedy.py
│   │   └── simulated_annealing.py
│   ├── services/
│   │   ├── scenario_generator.py
│   │   ├── experiment_runner.py
│   │   └── plotter.py
│   ├── api/routes.py
│   └── main.py
├── tests/
├── scripts/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/generate-scenario` | Generate synthetic scenario |
| `POST` | `/api/v1/solve` | Solve with one algorithm |
| `POST` | `/api/v1/compare` | Compare all three algorithms |

---

## Algorithms

| Algorithm | Strategy | Constraints |
|-----------|----------|-------------|
| **Naive** | Original list order | Checked post-hoc |
| **Greedy** | Nearest-neighbour + lookahead | Respected during build |
| **SA** | Greedy warm-start + local search | Penalised in objective |

**SA objective:**
```
score = total_distance
      + skipped_orders × 200
      + constraint_violations × 5000
```

---

## Development

```bash
uv run ruff check app/ tests/
uv run pytest -v --cov=app --cov-report=term-missing
```

---

## Roadmap

- [x] Stage 1 — core models, naive & greedy, FastAPI, tests
- [x] Stage 2 — simulated annealing, experiment runner, plots
- [x] Stage 3 — Docker, GitHub Actions CI, README
- [ ] Stage 4 (optional) — OR-Tools, time windows, multi-vehicle
