"""
Agent API 路由模块。

提供同步和异步的 Agent 调用端点，包括流式响应支持。
"""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

router = APIRouter()


# --- 认证依赖 ---

async def _verify_api_key(request: Request) -> None:
    """验证 API Key（如配置了 API_KEY 环境变量）。"""
    import os
    api_key = os.getenv("API_KEY")
    if not api_key:
        return

    provided = request.headers.get("X-API-Key")
    if not provided or provided != api_key:
        raise HTTPException(status_code=403, detail="无效的 API Key")


# --- 消息转换 ---

_MSG_TYPE_MAP = {
    "user": HumanMessage,
    "human": HumanMessage,
    "assistant": AIMessage,
    "ai": AIMessage,
    "system": SystemMessage,
}


def _convert_messages(raw_messages: list[dict[str, Any]]) -> list:
    """将原始字典消息列表转换为 LangChain Message 对象列表。"""
    converted = []
    for msg in raw_messages:
        if isinstance(msg, dict):
            msg_type = msg.get("role", msg.get("type", "user")).lower()
            content = msg.get("content", "")
            cls = _MSG_TYPE_MAP.get(msg_type, HumanMessage)
            converted.append(cls(content=content))
        else:
            converted.append(msg)
    return converted


# --- 辅助函数 ---

def _parse_request_body(body: dict[str, Any]) -> tuple[list, dict[str, Any], dict[str, Any]]:
    """解析请求体，返回 messages, config, context。"""
    raw_messages = body.get("messages", [])
    config = body.get("config", {})
    context = body.get("context", {})
    messages = _convert_messages(raw_messages)
    return messages, config, context


def _format_agent_response(result: Any) -> dict[str, Any]:
    """格式化 Agent 的 invoke 结果。"""
    raw_messages = None
    if isinstance(result, dict):
        raw_messages = result.get("messages", [])
    elif hasattr(result, "messages"):
        raw_messages = result.messages

    if not raw_messages:
        return {"messages": []}

    messages = []
    for msg in raw_messages:
        if hasattr(msg, "content"):
            messages.append({
                "role": getattr(msg, "type", "assistant"),
                "content": msg.content,
            })
        elif isinstance(msg, dict):
            messages.append(msg)
        else:
            messages.append({"role": "unknown", "content": str(msg)})
    return {"messages": messages}


def _format_stream_chunk(chunk: Any) -> str:
    """格式化流式响应的单个 chunk。

    流式 chunk 格式: {stage_name: {messages: [...]}} 或 {messages: [...]}
    """
    if not isinstance(chunk, dict):
        return f'data: {json.dumps({"messages": []}, ensure_ascii=False)}\n\n'

    # 查找包含 messages 的数据（可能直接在 chunk 中，也可能在子 dict 中）
    raw_messages = None
    stage_name = None
    if "messages" in chunk:
        raw_messages = chunk["messages"]
        stage_name = "state"
    else:
        for key, value in chunk.items():
            if isinstance(value, dict) and "messages" in value:
                raw_messages = value["messages"]
                stage_name = key
                break

    if not raw_messages:
        return f'data: {json.dumps({"messages": []}, ensure_ascii=False)}\n\n'

    messages = []
    for msg in raw_messages:
        if hasattr(msg, "content") and not isinstance(msg, dict):
            messages.append({
                "role": getattr(msg, "type", "assistant"),
                "content": msg.content,
            })
        elif isinstance(msg, dict):
            messages.append(msg)
        else:
            messages.append({"role": "unknown", "content": str(msg)})

    data = {"stage": stage_name, "messages": messages}
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# --- 同步端点（通过 asyncio.to_thread 在线程池中运行）---

@router.post("/invoke", tags=["Agent"])
async def invoke(request: Request, body: dict[str, Any]):
    """同步调用 Agent（在线程池中运行以兼容异步 checkpointer）。"""
    await _verify_api_key(request)
    messages, config, context = _parse_request_body(body)

    agent = request.app.state.agent
    try:
        result = await asyncio.to_thread(
            agent.invoke,
            {"messages": messages},
            config=config,
            context=context,
        )
        return _format_agent_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {e}")


@router.post("/stream", tags=["Agent"])
async def stream(request: Request, body: dict[str, Any]):
    """同步流式响应，通过 SSE 返回（在线程池中运行）。"""
    await _verify_api_key(request)
    messages, config, context = _parse_request_body(body)

    agent = request.app.state.agent

    def _sync_stream():
        for chunk in agent.stream(
            {"messages": messages},
            config=config,
            context=context,
        ):
            yield _format_stream_chunk(chunk)
        yield "data: [DONE]\n\n"

    async def event_generator():
        loop = asyncio.get_event_loop()
        gen = _sync_stream()
        while True:
            try:
                chunk = await loop.run_in_executor(None, next, gen, None)
                if chunk is None:
                    break
                yield chunk
            except StopIteration:
                break
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
                yield "data: [DONE]\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --- 异步端点 ---

@router.post("/ainvoke", tags=["Agent"])
async def ainvoke(request: Request, body: dict[str, Any]):
    """异步调用 Agent。"""
    await _verify_api_key(request)
    messages, config, context = _parse_request_body(body)

    agent = request.app.state.agent
    try:
        result = await agent.ainvoke(
            {"messages": messages},
            config=config,
            context=context,
        )
        return _format_agent_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {e}")


@router.post("/astream", tags=["Agent"])
async def astream(request: Request, body: dict[str, Any]):
    """异步流式响应，通过 SSE 返回。"""
    await _verify_api_key(request)
    messages, config, context = _parse_request_body(body)

    agent = request.app.state.agent

    async def event_generator():
        try:
            async for chunk in agent.astream(
                {"messages": messages},
                config=config,
                context=context,
            ):
                yield _format_stream_chunk(chunk)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
