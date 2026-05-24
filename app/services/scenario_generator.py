import random

from app.core.models import Depot, Order, Point, Scenario


def generate_scenario(
    num_orders: int = 10,
    seed: int = 42,
    grid_size: float = 100.0,
) -> Scenario:
    """Generate a synthetic 2-D scenario with random order locations."""
    rng = random.Random(seed)
    depot = Depot(location=Point(x=grid_size / 2, y=grid_size / 2))

    orders = [
        Order(
            id=i,
            location=Point(
                x=rng.uniform(0, grid_size),
                y=rng.uniform(0, grid_size),
            ),
            demand=1,
            service_time=rng.uniform(3.0, 10.0),
        )
        for i in range(1, num_orders + 1)
    ]

    return Scenario(depot=depot, orders=orders)
