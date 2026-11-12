"""Tests for the /health endpoint.

Run with:  uv run pytest -v
"""

from fastapi.testclient import TestClient

from app.main import app

# TestClient lets you call the app in-process, without starting a real server.
client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

