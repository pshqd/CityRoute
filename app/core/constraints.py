from app.core.models import ConstraintConfig, Route


def is_feasible(route: Route, constraints: ConstraintConfig) -> bool:
    """Return True if route satisfies all hard constraints."""
    if route.total_distance > constraints.max_distance:
        return False
    if route.total_time > constraints.max_route_time:
        return False
    return True


def count_violations(route: Route, constraints: ConstraintConfig) -> int:
    """Count the number of violated constraints."""
    violations = 0
    if route.total_distance > constraints.max_distance:
        violations += 1
    if route.total_time > constraints.max_route_time:
        violations += 1
    return violations
