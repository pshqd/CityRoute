from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_scenario_default():
    response = client.post("/api/v1/generate-scenario")
    assert response.status_code == 200
    data = response.json()
    assert "depot" in data
    assert "orders" in data
    assert len(data["orders"]) == 10


def test_generate_scenario_custom():
    response = client.post("/api/v1/generate-scenario?num_orders=5&seed=7")
    assert response.status_code == 200
    assert len(response.json()["orders"]) == 5


def test_solve_greedy():
    response = client.post(
        "/api/v1/solve",
        json={
            "scenario": {
                "depot": {"location": {"x": 50, "y": 50}},
                "orders": [
                    {"id": 1, "location": {"x": 10, "y": 20}, "demand": 1, "service_time": 5},
                    {"id": 2, "location": {"x": 80, "y": 60}, "demand": 1, "service_time": 5},
                ],
            },
            "algorithm": "greedy",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "greedy"
    assert data["route"]["served_orders"] == 2


def test_compare_endpoint():
    response = client.post(
        "/api/v1/compare",
        json={
            "scenario": {
                "depot": {"location": {"x": 50, "y": 50}},
                "orders": [
                    {"id": 1, "location": {"x": 10, "y": 20}, "demand": 1, "service_time": 5},
                    {"id": 2, "location": {"x": 80, "y": 60}, "demand": 1, "service_time": 5},
                ],
            },
            "algorithm": "greedy",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "naive" in data
    assert "greedy" in data
