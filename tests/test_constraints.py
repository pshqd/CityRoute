import pytest

from app.core.constraints import count_violations, is_feasible
from app.core.models import ConstraintConfig, Route


@pytest.fixture
def default_constraints():
    return ConstraintConfig(max_distance=200.0, max_route_time=200.0, capacity=10)


def test_is_feasible_true(default_constraints):
    route = Route(
        order_ids=[1, 2],
        total_distance=100.0,
        total_time=120.0,
        served_orders=2,
        feasible=True,
    )
    assert is_feasible(route, default_constraints) is True


def test_is_feasible_false_distance(default_constraints):
    route = Route(
        order_ids=[1, 2],
        total_distance=250.0,
        total_time=120.0,
        served_orders=2,
        feasible=True,
    )
    assert is_feasible(route, default_constraints) is False


def test_is_feasible_false_time(default_constraints):
    route = Route(
        order_ids=[1, 2],
        total_distance=100.0,
        total_time=300.0,
        served_orders=2,
        feasible=True,
    )
    assert is_feasible(route, default_constraints) is False


def test_count_violations_zero(default_constraints):
    route = Route(
        order_ids=[1],
        total_distance=50.0,
        total_time=60.0,
        served_orders=1,
        feasible=True,
    )
    assert count_violations(route, default_constraints) == 0


def test_count_violations_both(default_constraints):
    route = Route(
        order_ids=[1],
        total_distance=300.0,
        total_time=300.0,
        served_orders=1,
        feasible=False,
    )
    assert count_violations(route, default_constraints) == 2
