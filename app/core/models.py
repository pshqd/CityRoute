from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class Order(BaseModel):
    id: int
    location: Point
    demand: int = 1
    service_time: float = 5.0  # minutes


class Depot(BaseModel):
    location: Point


class ConstraintConfig(BaseModel):
    max_route_time: float = 500.0   # minutes
    max_distance: float = 500.0     # km / units
    capacity: int = 999


class Scenario(BaseModel):
    depot: Depot
    orders: List[Order] = Field(default_factory=list)


class Route(BaseModel):
    order_ids: List[int] = Field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    served_orders: int = 0
    feasible: bool = True


class SolveRequest(BaseModel):
    scenario: Scenario
    constraints: ConstraintConfig = Field(default_factory=ConstraintConfig)
    algorithm: Literal["naive", "greedy"] = "greedy"


class SolveResult(BaseModel):
    algorithm: str
    route: Route
    service_rate: float
    constraint_violations: int
