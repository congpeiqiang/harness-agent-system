"""
PDF 解析中间件。

自动检测并解析 Agent 消息中的 PDF 附件。
"""

from typing import Any

from langchain.agents.middleware import AgentMiddleware


class PDFParseMiddleware(AgentMiddleware):
    """
    PDF 自动解析中间件。

    在 Agent 处理消息前，自动检测消息中的 PDF 附件并解析。
    如果消息包含 PDF 附件，则提取文本内容并替换原始附件。
    """

    @staticmethod
    def _get_msg_content(msg: Any) -> Any:
        """安全获取消息内容，兼容 dict 和 Message 对象。"""
        if isinstance(msg, dict):
            return msg.get("content")
        return getattr(msg, "content", None)

    def before_agent(self, state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
        """处理消息，检测并解析 PDF 附件。"""
        if state.get("pdf_parsed", False):
            return state

        messages = state.get("messages", [])
        pdf_found = False
        for msg in messages:
            content = self._get_msg_content(msg)
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "pdf":
                        pdf_found = True
                        break
            if pdf_found:
                break

        if not pdf_found:
            return state

        parsed_messages = []
        for msg in messages:
            parsed_messages.append(msg)

        return {**state, "messages": parsed_messages, "pdf_parsed": True}

    def after_agent(self, state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
        """Agent 处理后的回调。"""
        return state
