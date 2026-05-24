from app.core.metrics import compute_metrics, service_rate
from app.core.models import Route


def make_route(served: int, distance: float = 0.0, time: float = 0.0) -> Route:
    return Route(
        order_ids=list(range(1, served + 1)),
        total_distance=distance,
        total_time=time,
        served_orders=served,
        feasible=True,
    )


def test_service_rate_full():
    route = make_route(served=5)
    assert service_rate(route, 5) == 1.0


def test_service_rate_partial():
    route = make_route(served=3)
    assert service_rate(route, 5) == 0.6


def test_service_rate_zero_total():
    route = make_route(served=0)
    assert service_rate(route, 0) == 0.0


def test_compute_metrics_keys():
    route = make_route(served=4, distance=120.5, time=150.0)
    metrics = compute_metrics(route, total_orders=5)
    expected_keys = {
        "total_distance",
        "total_time",
        "served_orders",
        "total_orders",
        "service_rate",
        "feasible",
    }
    assert expected_keys == set(metrics.keys())
