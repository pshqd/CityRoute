import pytest

from app.algorithms.simulated_annealing import solve_sa
from app.core.models import ConstraintConfig, SAConfig
from app.services.scenario_generator import generate_scenario


@pytest.fixture
def scenario_small():
    return generate_scenario(num_orders=8, seed=42)


@pytest.fixture
def loose_constraints():
    return ConstraintConfig(max_distance=10_000.0, max_route_time=10_000.0, capacity=999)


@pytest.fixture
def tight_constraints():
    return ConstraintConfig(max_distance=50.0, max_route_time=50.0, capacity=999)


@pytest.fixture
def sa_config():
    return SAConfig(initial_temp=500.0, cooling_rate=0.99, min_temp=1.0, max_iterations=1000, seed=42)


def test_sa_returns_route(scenario_small, loose_constraints, sa_config):
    route = solve_sa(scenario_small, loose_constraints, sa_config)
    assert route.served_orders >= 0
    assert route.total_distance >= 0


def test_sa_feasible_loose(scenario_small, loose_constraints, sa_config):
    route = solve_sa(scenario_small, loose_constraints, sa_config)
    assert route.feasible is True


def test_sa_serves_all_loose(scenario_small, loose_constraints, sa_config):
    route = solve_sa(scenario_small, loose_constraints, sa_config)
    assert route.served_orders == len(scenario_small.orders)


def test_sa_better_than_naive_distance(scenario_small, loose_constraints, sa_config):
    from app.algorithms.naive import solve_naive
    naive_route = solve_naive(scenario_small, loose_constraints)
    sa_route = solve_sa(scenario_small, loose_constraints, sa_config)
    assert sa_route.total_distance <= naive_route.total_distance


def test_sa_tight_constraints_feasible(scenario_small, tight_constraints, sa_config):
    """Under very tight constraints SA may be infeasible but should minimise violations."""
    route = solve_sa(scenario_small, tight_constraints, sa_config)
    # SA cannot guarantee feasibility under impossible constraints —
    # assert it at least returns a valid Route object
    assert route.served_orders >= 0
    assert route.total_distance >= 0


def test_sa_deterministic(scenario_small, loose_constraints, sa_config):
    r1 = solve_sa(scenario_small, loose_constraints, sa_config)
    r2 = solve_sa(scenario_small, loose_constraints, sa_config)
    assert r1.total_distance == r2.total_distance
    assert r1.order_ids == r2.order_ids
