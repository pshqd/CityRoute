from math import dist

from app.core.constraints import is_feasible
from app.core.models import ConstraintConfig, Route, Scenario


def solve_naive(scenario: Scenario, constraints: ConstraintConfig) -> Route:
    """
    Naive baseline: visit orders in original list order,
    return to depot at the end.
    """
    depot = (scenario.depot.location.x, scenario.depot.location.y)
    total_distance = 0.0
    total_time = 0.0
    order_ids = []
    current = depot

    for order in scenario.orders:
        nxt = (order.location.x, order.location.y)
        step = dist(current, nxt)
        total_distance += step
        total_time += step + order.service_time
        order_ids.append(order.id)
        current = nxt

    back = dist(current, depot)
    total_distance += back
    total_time += back

    route = Route(
        order_ids=order_ids,
        total_distance=total_distance,
        total_time=total_time,
        served_orders=len(order_ids),
    )
    route.feasible = is_feasible(route, constraints)
    return route
