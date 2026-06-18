"""
响应体定义模块。

定义 API 端点的响应体。
"""

from typing import Any


class InvokeResponse:
    """
    /invoke 和 /ainvoke 响应体

    Attributes:
        messages: 处理后的消息列表
    """

    def __init__(self, messages: list[dict[str, Any]] | None = None):
        self.messages = messages or []

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {"messages": self.messages}


class StreamResponse:
    """
    /stream 和 /astream 响应体

    Attributes:
        messages: 消息列表
        tools: 工具调用信息
        is_last_message: 是否为最后一条消息
        interrupt: 中断信息（人机交互时）
    """

    def __init__(
        self,
        messages: list[dict[str, Any]] | None = None,
        tools: list[dict[str, Any]] | None = None,
        is_last_message: bool = False,
        interrupt: dict[str, Any] | None = None,
    ):
        self.messages = messages or []
        self.tools = tools or []
        self.is_last_message = is_last_message
        self.interrupt = interrupt

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "messages": self.messages,
            "tools": self.tools,
            "is_last_message": self.is_last_message,
            "interrupt": self.interrupt,
        }


class HealthResponse:
    """
    /health 响应体

    Attributes:
        status: 服务状态
        version: 版本号
        uptime_seconds: 运行时长（秒）
    """

    def __init__(self, status: str = "healthy", version: str = "0.1.0", uptime_seconds: float = 0.0):
        self.status = status
        self.version = version
        self.uptime_seconds = uptime_seconds

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "status": self.status,
            "version": self.version,
            "uptime_seconds": round(self.uptime_seconds, 2),
        }


class MetricsResponse:
    """
    /metrics 响应体

    Attributes:
        uptime_seconds: 运行时长（秒）
        version: 版本号
    """

    def __init__(self, uptime_seconds: float = 0.0, version: str = "0.1.0"):
        self.uptime_seconds = uptime_seconds
        self.version = version

    def model_dump(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "uptime_seconds": round(self.uptime_seconds, 2),
            "version": self.version,
        }
