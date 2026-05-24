from fastapi import APIRouter, Query

from app.algorithms.greedy import solve_greedy
from app.algorithms.naive import solve_naive
from app.core.metrics import compute_metrics
from app.core.models import Scenario, SolveRequest, SolveResult
from app.services.scenario_generator import generate_scenario

router = APIRouter()


@router.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


@router.post("/generate-scenario", response_model=Scenario, tags=["scenario"])
def generate_scenario_endpoint(
    num_orders: int = Query(default=10, ge=1, le=100),
    seed: int = Query(default=42),
) -> Scenario:
    return generate_scenario(num_orders=num_orders, seed=seed)


@router.post("/solve", response_model=SolveResult, tags=["solver"])
def solve(request: SolveRequest) -> SolveResult:
    if request.algorithm == "naive":
        route = solve_naive(request.scenario, request.constraints)
    else:
        route = solve_greedy(request.scenario, request.constraints)

    metrics = compute_metrics(route, total_orders=len(request.scenario.orders))

    from app.core.constraints import count_violations
    violations = count_violations(route, request.constraints)

    return SolveResult(
        algorithm=request.algorithm,
        route=route,
        service_rate=metrics["service_rate"],
        constraint_violations=violations,
    )


@router.post("/compare", tags=["solver"])
def compare(request: SolveRequest) -> dict:
    """Run both algorithms on the same scenario and return side-by-side metrics."""
    total = len(request.scenario.orders)

    naive_route = solve_naive(request.scenario, request.constraints)
    greedy_route = solve_greedy(request.scenario, request.constraints)

    from app.core.constraints import count_violations

    return {
        "naive": {
            **compute_metrics(naive_route, total),
            "constraint_violations": count_violations(naive_route, request.constraints),
        },
        "greedy": {
            **compute_metrics(greedy_route, total),
            "constraint_violations": count_violations(greedy_route, request.constraints),
        },
    }
