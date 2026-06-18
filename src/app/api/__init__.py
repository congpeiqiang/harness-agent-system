"""
Agent API 路由模块。

提供同步和异步的 Agent 调用端点，包括流式响应支持。
"""

import json
import time
from typing import Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

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


# --- 辅助函数 ---

def _parse_request_body(body: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """解析请求体，返回 messages, config, context。"""
    messages = body.get("messages", [])
    config = body.get("config", {})
    context = body.get("context", {})
    return messages, config, context


def _format_agent_response(result: Any) -> dict[str, Any]:
    """格式化 Agent 的 invoke 结果。"""
    if hasattr(result, "messages"):
        messages = []
        for msg in result.messages:
            if hasattr(msg, "content"):
                messages.append({
                    "role": getattr(msg, "type", "assistant"),
                    "content": msg.content,
                })
            else:
                messages.append(msg)
        return {"messages": messages}
    return {"messages": []}


def _format_stream_chunk(chunk: Any) -> str:
    """格式化流式响应的单个 chunk。"""
    if hasattr(chunk, "messages"):
        messages = []
        for msg in chunk.messages:
            if hasattr(msg, "content"):
                messages.append({
                    "role": getattr(msg, "type", "assistant"),
                    "content": msg.content,
                })
            else:
                messages.append(msg)
        data = {"messages": messages}
    else:
        data = {"messages": []}
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# --- 同步端点 ---

@router.post("/invoke", tags=["Agent"])
async def invoke(request: Request, body: dict[str, Any]):
    """同步调用 Agent。"""
    await _verify_api_key(request)
    messages, config, context = _parse_request_body(body)

    agent = request.app.state.agent
    try:
        result = agent.invoke(
            {"messages": messages},
            config=config,
            context=context,
        )
        return _format_agent_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {e}")


@router.post("/stream", tags=["Agent"])
async def stream(request: Request, body: dict[str, Any]):
    """同步流式响应，通过 SSE 返回。"""
    await _verify_api_key(request)
    messages, config, context = _parse_request_body(body)

    agent = request.app.state.agent

    async def event_generator():
        try:
            for chunk in agent.stream(
                {"messages": messages},
                config=config,
                context=context,
            ):
                yield _format_stream_chunk(chunk)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
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
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
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
