"""
Agent 工厂模块，支持可插拔的检查点和存储。

本模块构建 LangGraph Agent，配置中间件、工具和持久化层。
"""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    ToolCallLimitMiddleware,
    before_model,
)
from langchain.chat_models import init_chat_model
from langgraph.runtime import Runtime

from app.core.config import settings
from app.core.state import CustomState, ContextState
from app.middleware.pdf_parse_middleware import PDFParseMiddleware
from app.tools import (
    get_weather,
    parse_pdf_from_content,
    parse_pdf_from_file,
    parse_pdf_from_url,
)
from app.tools.mcp_client_builder import get_mcp_tools_async

load_dotenv()


# ---------------------------------------------------------------------------
# 模型调用前的钩子（用于日志记录）
# ---------------------------------------------------------------------------

@before_model
def print_hook(state: AgentState, runtime: Runtime):
    """在每次模型调用前记录执行信息。"""
    execution_info = getattr(runtime, "execution_info", None)
    server_info = getattr(runtime, "server_info", None)
    thread_id = getattr(execution_info, "thread_id", "未知") if execution_info else "未知"
    assistant_id = getattr(server_info, "assistant_id", "未知") if server_info else "未知"
    print(f"[agent] 线程: {thread_id} | 助手: {assistant_id}")
    return state


# ---------------------------------------------------------------------------
# 中间件配置
# ---------------------------------------------------------------------------

# 人机交互中间件：需要审批的操作
human_in_loop_middleware = [
    HumanInTheLoopMiddleware(
        interrupt_on={
            "customer_login_submit_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
            "submit_register_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
            "paypal_express_start_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
            "paypal_express_submit_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
            "paypal_standard_start_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
            "checkmoney_start_tool": {"allowed_decisions": ["approve", "edit", "reject"]},
        }
    )
]

# 工具调用限制中间件
tool_call_limit_middleware = [
    ToolCallLimitMiddleware(
        tool_name="get_weather_async",
        thread_limit=20,
        run_limit=3,
    ),
]


# ---------------------------------------------------------------------------
# 模型初始化
# ---------------------------------------------------------------------------

_model = None


def _get_model():
    """延迟初始化 LLM 模型。"""
    global _model
    if _model is None:
        _model = init_chat_model(
            os.getenv("DEEPSEEK_MODEL", settings.deepseek_model),
            model_provider=os.getenv("DEEPSEEK_MODEL_PROVIDER", "deepseek"),
            api_key=os.getenv("DEEPSEEK_API_KEY", settings.deepseek_api_key),
            base_url=os.getenv("DEEPSEEK_BASE_URL", settings.deepseek_base_url),
        )
    return _model


# ---------------------------------------------------------------------------
# 工具收集
# ---------------------------------------------------------------------------

async def get_all_tools_async() -> list[Any]:
    """收集所有可用工具（内置 + MCP）。"""
    tools = [
        get_weather,
        parse_pdf_from_file,
        parse_pdf_from_content,
        parse_pdf_from_url,
    ]
    mcp_tools = await get_mcp_tools_async()
    tools.extend(mcp_tools)
    return tools


def get_all_tools() -> list[Any]:
    """get_all_tools_async 的同步版本。"""
    tools = [
        get_weather,
        parse_pdf_from_file,
        parse_pdf_from_content,
        parse_pdf_from_url,
    ]
    mcp_tools = asyncio.run(get_mcp_tools_async())
    tools.extend(mcp_tools)
    return tools


# ---------------------------------------------------------------------------
# Agent 构建器
# ---------------------------------------------------------------------------

async def build_agent(checkpointer: Any, store: Any) -> Any:
    """构建并返回 Agent 实例，使用给定的持久化层。"""
    model = _get_model()
    tools = await get_all_tools_async()

    return create_agent(
        model=model,
        state_schema=CustomState,
        context_schema=ContextState,
        tools=tools,
        system_prompt="你是一个有帮助的助手",
        middleware=[
            print_hook,
            PDFParseMiddleware(),
            ModelFallbackMiddleware(
                os.getenv("DEEPSEEK_MODEL", settings.deepseek_model),
                os.getenv("DEEPSEEK_MODEL", settings.deepseek_model),
            ),
            *human_in_loop_middleware,
            *tool_call_limit_middleware,
        ],
        checkpointer=checkpointer,
        store=store,
    )
