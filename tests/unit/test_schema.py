"""
Schema 模块测试。

测试请求和响应模型的初始化和序列化。
"""

import pytest
from app.schema.request import InvokeRequest, StreamRequest, BatchRequest, ThreadStateUpdate
from app.schema.response import InvokeResponse, StreamResponse, HealthResponse, MetricsResponse


class TestRequestModels:
    """请求模型测试。"""

    def test_invoke_request_init(self):
        """测试 InvokeRequest 初始化。"""
        req = InvokeRequest(
            messages=[{"role": "user", "content": "你好"}],
            config={"configurable": {"thread_id": "test"}},
        )
        data = req.model_dump()
        assert len(data["messages"]) == 1
        assert data["messages"][0]["role"] == "user"
        assert data["config"]["configurable"]["thread_id"] == "test"

    def test_stream_request_init(self):
        """测试 StreamRequest 初始化。"""
        req = StreamRequest(
            messages=[{"role": "user", "content": "测试"}],
            context={"user_id": "u123"},
        )
        data = req.model_dump()
        assert data["context"]["user_id"] == "u123"

    def test_batch_request_init(self):
        """测试 BatchRequest 初始化。"""
        req = BatchRequest(requests=[
            InvokeRequest(messages=[{"role": "user", "content": "a"}]),
            InvokeRequest(messages=[{"role": "user", "content": "b"}]),
        ])
        data = req.model_dump()
        assert len(data["requests"]) == 2

    def test_thread_state_update_init(self):
        """测试 ThreadStateUpdate 初始化。"""
        update = ThreadStateUpdate(values={"key": "value"})
        data = update.model_dump()
        assert data["values"]["key"] == "value"

    def test_default_values(self):
        """测试默认值。"""
        req = InvokeRequest()
        data = req.model_dump()
        assert data["messages"] == []
        assert data["config"] == {}
        assert data["context"] == {}


class TestResponseModels:
    """响应模型测试。"""

    def test_invoke_response(self):
        """测试 InvokeResponse。"""
        resp = InvokeResponse(messages=[{"role": "assistant", "content": "你好"}])
        data = resp.model_dump()
        assert len(data["messages"]) == 1

    def test_health_response(self):
        """测试 HealthResponse。"""
        resp = HealthResponse(status="healthy", version="0.1.0", uptime_seconds=123.456)
        data = resp.model_dump()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["uptime_seconds"] == 123.46

    def test_stream_response(self):
        """测试 StreamResponse。"""
        resp = StreamResponse(
            messages=[{"role": "assistant", "content": "流式响应"}],
            is_last_message=True,
        )
        data = resp.model_dump()
        assert data["is_last_message"] is True
        assert len(data["messages"]) == 1

    def test_metrics_response(self):
        """测试 MetricsResponse。"""
        resp = MetricsResponse(uptime_seconds=100.123, version="0.1.0")
        data = resp.model_dump()
        assert data["uptime_seconds"] == 100.12
        assert data["version"] == "0.1.0"

    def test_default_response_values(self):
        """测试默认响应值。"""
        resp = InvokeResponse()
        data = resp.model_dump()
        assert data["messages"] == []
