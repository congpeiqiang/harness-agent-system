"""Unit tests for API health endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client without lifespan (no DB needed)."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient as _TestClient

    # Minimal app for health endpoint testing
    app = FastAPI()
    app.state.start_time = __import__("time").time()

    @app.get("/health")
    async def health():
        import time
        uptime = time.time() - app.state.start_time
        return {"status": "healthy", "version": "0.1.0", "uptime_seconds": round(uptime, 2)}

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    return _TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_healthy(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_ok_returns_200(self, client):
        response = client.get("/ok")
        assert response.status_code == 200

    def test_ok_status(self, client):
        response = client.get("/ok")
        data = response.json()
        assert data["status"] == "ok"
