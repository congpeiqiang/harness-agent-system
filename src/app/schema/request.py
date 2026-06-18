"""
请求体定义模块。

定义 API 端点的请求体，使用 Pydantic 进行数据验证。
"""

from typing import Any


class InvokeRequest:
    """
    请求体

    Attributes:
        messages: 对话消息列表，每个消息包含 role 和 content 字段
        config: 配置参数，包含 configurable 等设置
        context: 上下文信息
    """

    def __init__(
        self,
        messages: list[dict[str, Any]] | None = None,
        config: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ):
        self.messages = messages or []
        self.config = config or {}
        self.context = context or {}

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "messages": self.messages,
            "config": self.config,
            "context": self.context,
        }


class StreamRequest:
    """
    流式请求体

    Attributes:
        messages: 对话消息列表
        config: 配置参数
        context: 上下文信息
    """

    def __init__(
        self,
        messages: list[dict[str, Any]] | None = None,
        config: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ):
        self.messages = messages or []
        self.config = config or {}
        self.context = context or {}

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "messages": self.messages,
            "config": self.config,
            "context": self.context,
        }


class BatchRequest:
    """
    批量请求体

    Attributes:
        requests: InvokeRequest 列表
    """

    def __init__(self, requests: list[InvokeRequest] | None = None):
        self.requests = requests or []

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {"requests": [r.model_dump() for r in self.requests]}


class ThreadStateUpdate:
    """
    线程状态更新请求体

    Attributes:
        values: 要更新的状态值
    """

    def __init__(self, values: dict[str, Any] | None = None):
        self.values = values or {}

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {"values": self.values}
