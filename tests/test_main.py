from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sum_endpoint():
    response = client.post("/sum", json={"a": 8, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"operation": "sum", "result": 10}


def test_subtract_endpoint():
    response = client.post("/subtract", json={"a": 8, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"operation": "subtract", "result": 6}


def test_multiply_endpoint():
    response = client.post("/multiply", json={"a": 8, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"operation": "multiply", "result": 16}


def test_divide_endpoint():
    response = client.post("/divide", json={"a": 8, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"operation": "divide", "result": 4}


def test_divide_by_zero_returns_400():
    response = client.post("/divide", json={"a": 8, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "division by zero is not allowed"}
