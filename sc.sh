#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="CityRoute"
PYTHON_VERSION="3.11"

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

uv init --package --python "$PYTHON_VERSION"

mkdir -p app/api
mkdir -p app/core
mkdir -p app/algorithms
mkdir -p app/services
mkdir -p data/scenarios
mkdir -p results
mkdir -p notebooks
mkdir -p tests
mkdir -p scripts

touch app/__init__.py
touch app/api/__init__.py
touch app/core/__init__.py
touch app/algorithms/__init__.py
touch app/services/__init__.py

uv add fastapi "uvicorn[standard]" pydantic numpy pandas networkx scipy matplotlib plotly
uv add --dev pytest pytest-cov httpx ruff

cat > app/main.py <<'EOF'
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Vehicle Routing Lite", version="0.1.0")
app.include_router(router)
EOF

cat > app/api/routes.py <<'EOF'
from fastapi import APIRouter
from app.core.models import Scenario, SolveRequest
from app.services.scenariogenerator import generate_scenario
from app.algorithms.naive import solve_naive
from app.algorithms.greedy import solve_greedy

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/generate-scenario", response_model=Scenario)
def generate_scenario_endpoint(num_orders: int = 10, seed: int = 42):
    return generate_scenario(num_orders=num_orders, seed=seed)

@router.post("/solve")
def solve(request: SolveRequest):
    if request.algorithm == "naive":
        return solve_naive(request.scenario, request.constraints)
    if request.algorithm == "greedy":
        return solve_greedy(request.scenario, request.constraints)
    return {"error": f"Unsupported algorithm: {request.algorithm}"}
EOF

cat > app/core/models.py <<'EOF'
from typing import List, Literal
from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class Order(BaseModel):
    id: int
    location: Point
    demand: int = 1
    service_time: float = 5.0


class Depot(BaseModel):
    location: Point


class ConstraintConfig(BaseModel):
    max_route_time: float = 500.0
    max_distance: float = 500.0
    capacity: int = 999


class Scenario(BaseModel):
    depot: Depot
    orders: List[Order] = Field(default_factory=list)


class Route(BaseModel):
    order_ids: List[int] = Field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    served_orders: int = 0
    feasible: bool = True


class SolveRequest(BaseModel):
    scenario: Scenario
    constraints: ConstraintConfig
    algorithm: Literal["naive", "greedy"]
EOF

cat > app/core/constraints.py <<'EOF'
from app.core.models import Route, ConstraintConfig


def is_feasible(route: Route, constraints: ConstraintConfig) -> bool:
    if route.total_distance > constraints.max_distance:
        return False
    if route.total_time > constraints.max_route_time:
        return False
    return True
EOF

cat > app/core/metrics.py <<'EOF'
from app.core.models import Route


def service_rate(route: Route, total_orders: int) -> float:
    if total_orders == 0:
        return 0.0
    return route.served_orders / total_orders
EOF

cat > app/algorithms/naive.py <<'EOF'
from math import dist
from app.core.models import Scenario, ConstraintConfig, Route
from app.core.constraints import is_feasible


def solve_naive(scenario: Scenario, constraints: ConstraintConfig) -> dict:
    depot = (scenario.depot.location.x, scenario.depot.location.y)
    total_distance = 0.0
    total_time = 0.0
    order_ids = []

    current = depot
    for order in scenario.orders:
        nxt = (order.location.x, order.location.y)
        total_distance += dist(current, nxt)
        total_time += dist(current, nxt) + order.service_time
        order_ids.append(order.id)
        current = nxt

    total_distance += dist(current, depot)
    total_time += dist(current, depot)

    route = Route(
        order_ids=order_ids,
        total_distance=total_distance,
        total_time=total_time,
        served_orders=len(order_ids),
        feasible=True,
    )
    route.feasible = is_feasible(route, constraints)
    return route.model_dump()
EOF

cat > app/algorithms/greedy.py <<'EOF'
from math import dist
from app.core.models import Scenario, ConstraintConfig, Route
from app.core.constraints import is_feasible


def solve_greedy(scenario: Scenario, constraints: ConstraintConfig) -> dict:
    depot = (scenario.depot.location.x, scenario.depot.location.y)
    remaining = scenario.orders[:]
    current = depot
    total_distance = 0.0
    total_time = 0.0
    order_ids = []

    while remaining:
        nearest = min(
            remaining,
            key=lambda o: dist(current, (o.location.x, o.location.y))
        )
        nxt = (nearest.location.x, nearest.location.y)
        step = dist(current, nxt)

        projected_distance = total_distance + step + dist(nxt, depot)
        projected_time = total_time + step + nearest.service_time + dist(nxt, depot)

        if projected_distance > constraints.max_distance or projected_time > constraints.max_route_time:
            break

        total_distance += step
        total_time += step + nearest.service_time
        order_ids.append(nearest.id)
        current = nxt
        remaining.remove(nearest)

    total_distance += dist(current, depot)
    total_time += dist(current, depot)

    route = Route(
        order_ids=order_ids,
        total_distance=total_distance,
        total_time=total_time,
        served_orders=len(order_ids),
        feasible=True,
    )
    route.feasible = is_feasible(route, constraints)
    return route.model_dump()
EOF

cat > app/services/scenariogenerator.py <<'EOF'
import random
from app.core.models import Scenario, Depot, Order, Point


def generate_scenario(num_orders: int = 10, seed: int = 42) -> Scenario:
    random.seed(seed)
    depot = Depot(location=Point(x=50.0, y=50.0))
    orders = []

    for i in range(1, num_orders + 1):
        orders.append(
            Order(
                id=i,
                location=Point(
                    x=random.uniform(0, 100),
                    y=random.uniform(0, 100),
                ),
                demand=1,
                service_time=random.uniform(3, 10),
            )
        )

    return Scenario(depot=depot, orders=orders)
EOF

cat > app/services/graphbuilder.py <<'EOF'
import networkx as nx
from app.core.models import Scenario


def build_graph(scenario: Scenario) -> nx.Graph:
    graph = nx.Graph()
    graph.add_node("depot", x=scenario.depot.location.x, y=scenario.depot.location.y)

    for order in scenario.orders:
        graph.add_node(order.id, x=order.location.x, y=order.location.y)

    return graph
EOF

cat > scripts/generatescenarios.py <<'EOF'
import json
from pathlib import Path
from app.services.scenariogenerator import generate_scenario


def main():
    scenario = generate_scenario(num_orders=10, seed=42)
    out = Path("data/scenarios/scenario_seed_42.json")
    out.write_text(scenario.model_dump_json(indent=2), encoding="utf-8")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
EOF

cat > scripts/runexperiments.py <<'EOF'
from app.services.scenariogenerator import generate_scenario
from app.core.models import ConstraintConfig
from app.algorithms.naive import solve_naive
from app.algorithms.greedy import solve_greedy


def main():
    scenario = generate_scenario(num_orders=15, seed=42)
    constraints = ConstraintConfig(max_route_time=500.0, max_distance=500.0, capacity=999)

    naive = solve_naive(scenario, constraints)
    greedy = solve_greedy(scenario, constraints)

    print({"naive": naive, "greedy": greedy})


if __name__ == "__main__":
    main()
EOF

cat > tests/test_constraints.py <<'EOF'
from app.core.models import Route, ConstraintConfig
from app.core.constraints import is_feasible


def test_is_feasible_true():
    route = Route(order_ids=[1, 2], total_distance=100, total_time=120, served_orders=2, feasible=True)
    constraints = ConstraintConfig(max_distance=200, max_route_time=200, capacity=10)
    assert is_feasible(route, constraints) is True


def test_is_feasible_false():
    route = Route(order_ids=[1, 2], total_distance=300, total_time=120, served_orders=2, feasible=True)
    constraints = ConstraintConfig(max_distance=200, max_route_time=200, capacity=10)
    assert is_feasible(route, constraints) is False
EOF

cat > tests/test_metrics.py <<'EOF'
from app.core.models import Route
from app.core.metrics import service_rate


def test_service_rate():
    route = Route(order_ids=[1, 2, 3], served_orders=3, total_distance=0, total_time=0, feasible=True)
    assert service_rate(route, 5) == 0.6
EOF

cat > tests/test_algorithms.py <<'EOF'
from app.services.scenariogenerator import generate_scenario
from app.core.models import ConstraintConfig
from app.algorithms.naive import solve_naive
from app.algorithms.greedy import solve_greedy


def test_naive_returns_route_dict():
    scenario = generate_scenario(num_orders=5, seed=42)
    constraints = ConstraintConfig()
    result = solve_naive(scenario, constraints)
    assert "order_ids" in result
    assert "total_distance" in result


def test_greedy_returns_route_dict():
    scenario = generate_scenario(num_orders=5, seed=42)
    constraints = ConstraintConfig()
    result = solve_greedy(scenario, constraints)
    assert "order_ids" in result
    assert "total_distance" in result
EOF

cat > README.md <<'EOF'
# Vehicle Routing Lite

Research-oriented backend project for single-courier routing with constraints.

## Stack
- Python 3.11
- uv
- FastAPI
- NumPy, pandas, NetworkX, SciPy
- pytest

## Run
```bash
uv run uvicorn app.main:app --reload
```

## Test
```bash
uv run pytest
```

## Generate scenario
```bash
uv run python scripts/generatescenarios.py
```
EOF

cat > Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install uv && uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker-compose.yml <<'EOF'
services:
  api:
    build: .
    ports:
      - "8000:8000"
EOF

echo
echo "Done. Next steps:"
echo "cd $PROJECT_NAME"
echo "uv run pytest"
echo "uv run uvicorn app.main:app --reload"