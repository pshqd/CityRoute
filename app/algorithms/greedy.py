from math import dist

from app.core.constraints import is_feasible
from app.core.models import ConstraintConfig, Route, Scenario


def solve_greedy(scenario: Scenario, constraints: ConstraintConfig) -> Route:
    """
    Greedy nearest-neighbour: always pick the closest unvisited order
    that keeps the route within constraints.
    """
    depot = (scenario.depot.location.x, scenario.depot.location.y)
    remaining = list(scenario.orders)
    current = depot
    total_distance = 0.0
    total_time = 0.0
    order_ids = []

    while remaining:
        nearest = min(
            remaining,
            key=lambda o: dist(current, (o.location.x, o.location.y)),
        )
        nxt = (nearest.location.x, nearest.location.y)
        step = dist(current, nxt)

        # lookahead: check if adding this order keeps us feasible
        projected_distance = total_distance + step + dist(nxt, depot)
        projected_time = (
            total_time + step + nearest.service_time + dist(nxt, depot)
        )

        if (
            projected_distance > constraints.max_distance
            or projected_time > constraints.max_route_time
        ):
            remaining.remove(nearest)
            continue

        total_distance += step
        total_time += step + nearest.service_time
        order_ids.append(nearest.id)
        current = nxt
        remaining.remove(nearest)

    # return to depot
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
