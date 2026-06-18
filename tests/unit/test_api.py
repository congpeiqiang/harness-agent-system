"""
API 端点测试。

测试健康检查和 API 端点的响应。
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """创建测试客户端。"""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """健康检查端点测试。"""

    def test_ok_endpoint(self, client):
        """测试 /ok 端点。"""
        response = client.get("/ok")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint(self, client):
        """测试 /health 端点。"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_metrics_endpoint(self, client):
        """测试 /metrics 端点。"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "uptime_seconds" in data
        assert "version" in data


class TestAgentEndpoints:
    """Agent API 端点测试。"""

    def test_invoke_no_auth(self, client):
        """测试无认证调用 /invoke。"""
        response = client.post(
            "/agent/invoke",
            json={"messages": [{"role": "user", "content": "你好"}]},
        )
        # 可能返回 403（需要 API_KEY）或 500（Agent 未初始化）
        assert response.status_code in [403, 500]

    def test_stream_no_auth(self, client):
        """测试无认证调用 /stream。"""
        response = client.post(
            "/agent/stream",
            json={"messages": [{"role": "user", "content": "你好"}]},
        )
        assert response.status_code in [403, 500]
