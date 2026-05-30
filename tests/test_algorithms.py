import pytest

from app.algorithms.greedy import solve_greedy
from app.algorithms.naive import solve_naive
from app.core.models import ConstraintConfig
from app.services.scenario_generator import generate_scenario


@pytest.fixture
def scenario():
    return generate_scenario(num_orders=10, seed=42)


@pytest.fixture
def tight_constraints():
    return ConstraintConfig(
        max_distance=50.0,
        max_route_time=50.0,
        capacity=999,
    )


@pytest.fixture
def loose_constraints():
    return ConstraintConfig(
        max_distance=10_000.0,
        max_route_time=10_000.0,
        capacity=999,
    )


def test_naive_visits_all_orders(scenario, loose_constraints):
    route = solve_naive(scenario, loose_constraints)
    assert route.served_orders == len(scenario.orders)
    assert set(route.order_ids) == {o.id for o in scenario.orders}


def test_naive_returns_to_depot(scenario, loose_constraints):
    route = solve_naive(scenario, loose_constraints)
    assert route.total_distance > 0


def test_naive_tight_infeasible(scenario, tight_constraints):
    route = solve_naive(scenario, tight_constraints)
    assert route.feasible is False


def test_greedy_feasible_loose(scenario, loose_constraints):
    route = solve_greedy(scenario, loose_constraints)
    assert route.feasible is True
    assert route.served_orders == len(scenario.orders)


def test_greedy_respects_tight(scenario, tight_constraints):
    route = solve_greedy(scenario, tight_constraints)
    assert route.feasible is True


def test_greedy_better_distance(scenario, loose_constraints):
    naive_route = solve_naive(scenario, loose_constraints)
    greedy_route = solve_greedy(scenario, loose_constraints)
    assert greedy_route.total_distance <= naive_route.total_distance
