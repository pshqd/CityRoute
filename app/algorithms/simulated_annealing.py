"""Simulated Annealing solver for single-courier VRP.

Neighbourhood operators (applied at random each iteration):
  - swap:           exchange positions of two orders in the route
  - insert:         remove an order and reinsert it at another position
  - reverse_segment: reverse a contiguous slice of the route

Objective (to minimise):
  score = total_distance
        + skipped_orders * SKIP_PENALTY
        + constraint_violations * VIOLATION_PENALTY
"""
from __future__ import annotations

import math
import random
from copy import deepcopy
from math import dist
from typing import List

from app.core.constraints import count_violations, is_feasible
from app.core.models import ConstraintConfig, Order, Route, SAConfig, Scenario

SKIP_PENALTY = 500.0
VIOLATION_PENALTY = 1000.0


# ---------------------------------------------------------------------------
# Route evaluation helpers
# ---------------------------------------------------------------------------

def _evaluate(order_ids: List[int], orders_by_id: dict, depot: tuple, constraints: ConstraintConfig) -> tuple[float, Route]:
    """Compute total_distance, total_time and build a Route for a given order sequence."""
    total_distance = 0.0
    total_time = 0.0
    current = depot

    for oid in order_ids:
        o = orders_by_id[oid]
        nxt = (o.location.x, o.location.y)
        step = dist(current, nxt)
        total_distance += step
        total_time += step + o.service_time
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
    return total_distance, route


def _score(route: Route, total_orders: int, constraints: ConstraintConfig) -> float:
    skipped = total_orders - route.served_orders
    violations = count_violations(route, constraints)
    return route.total_distance + skipped * SKIP_PENALTY + violations * VIOLATION_PENALTY


# ---------------------------------------------------------------------------
# Neighbourhood operators
# ---------------------------------------------------------------------------

def _swap(order_ids: List[int], rng: random.Random) -> List[int]:
    if len(order_ids) < 2:
        return order_ids[:]
    ids = order_ids[:]
    i, j = rng.sample(range(len(ids)), 2)
    ids[i], ids[j] = ids[j], ids[i]
    return ids


def _insert(order_ids: List[int], rng: random.Random) -> List[int]:
    if len(order_ids) < 2:
        return order_ids[:]
    ids = order_ids[:]
    i = rng.randrange(len(ids))
    elem = ids.pop(i)
    j = rng.randrange(len(ids) + 1)
    ids.insert(j, elem)
    return ids


def _reverse_segment(order_ids: List[int], rng: random.Random) -> List[int]:
    if len(order_ids) < 2:
        return order_ids[:]
    ids = order_ids[:]
    i, j = sorted(rng.sample(range(len(ids)), 2))
    ids[i:j + 1] = ids[i:j + 1][::-1]
    return ids


_OPERATORS = [_swap, _insert, _reverse_segment]


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve_sa(scenario: Scenario, constraints: ConstraintConfig, sa_config: SAConfig) -> Route:
    """Solve using simulated annealing. Returns the best Route found."""
    rng = random.Random(sa_config.seed)

    orders_by_id = {o.id: o for o in scenario.orders}
    depot = (scenario.depot.location.x, scenario.depot.location.y)
    total_orders = len(scenario.orders)

    if total_orders == 0:
        return Route()

    # Initialise with greedy solution for a warm start
    from app.algorithms.greedy import solve_greedy
    greedy_route = solve_greedy(scenario, constraints)
    current_ids = greedy_route.order_ids[:]

    # If greedy skipped orders, add remaining at the end for SA to optimise
    served_ids = set(current_ids)
    unserved = [o.id for o in scenario.orders if o.id not in served_ids]
    current_ids = current_ids + unserved

    _, current_route = _evaluate(current_ids, orders_by_id, depot, constraints)
    current_score = _score(current_route, total_orders, constraints)

    best_ids = current_ids[:]
    best_route = current_route
    best_score = current_score

    temp = sa_config.initial_temp

    for _ in range(sa_config.max_iterations):
        if temp < sa_config.min_temp:
            break

        operator = rng.choice(_OPERATORS)
        candidate_ids = operator(current_ids, rng)

        _, candidate_route = _evaluate(candidate_ids, orders_by_id, depot, constraints)
        candidate_score = _score(candidate_route, total_orders, constraints)

        delta = candidate_score - current_score
        if delta < 0 or rng.random() < math.exp(-delta / temp):
            current_ids = candidate_ids
            current_route = candidate_route
            current_score = candidate_score

            if current_score < best_score:
                best_ids = current_ids[:]
                best_route = current_route
                best_score = current_score

        temp *= sa_config.cooling_rate

    return best_route
