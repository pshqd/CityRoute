from app.core.models import Route


def service_rate(route: Route, total_orders: int) -> float:
    """Fraction of orders successfully served."""
    if total_orders == 0:
        return 0.0
    return round(route.served_orders / total_orders, 4)


def compute_metrics(route: Route, total_orders: int) -> dict:
    """Return a dict of all key metrics for a solved route."""
    return {
        "total_distance": round(route.total_distance, 4),
        "total_time": round(route.total_time, 4),
        "served_orders": route.served_orders,
        "total_orders": total_orders,
        "service_rate": service_rate(route, total_orders),
        "feasible": route.feasible,
    }
