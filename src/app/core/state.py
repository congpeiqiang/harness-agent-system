"""
自定义 Agent 状态定义。

继承 LangGraph 的 Annotation 系统，添加应用特定状态字段。
"""

from typing import Any, Annotated
from operator import add

from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState, add_messages


class CustomState(MessagesState):
    """自定义状态，用于 Agent 的执行。"""
    pdf_parsed: bool = False
    parsed_content: str = ""
    attachments: list[dict[str, Any]] = []


class ContextState:
    """上下文状态定义。"""
    user_id: str = ""
    thread_id: str = ""
    permissions: list[str] = []
    metadata: dict[str, Any] = {}
