"""Agent RESTful endpoints: invoke, ainvoke, stream, astream."""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.schema.request import InvokeRequest, StreamRequest
from app.core.state import ContextState

router = APIRouter()


def _build_context(ctx_dict: dict[str, Any]) -> ContextState | None:
    """Build ContextState from request dict."""
    if not ctx_dict:
        return None
    return ContextState(**ctx_dict)


def _build_input(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build agent input from messages."""
    return {"messages": messages}


def _default_agent_kwargs() -> dict[str, Any]:
    """Default kwargs for agent invocation."""
    return {"stream_mode": "values", "version": "v2"}


@router.post("/invoke")
async def agent_invoke(request: InvokeRequest, req: Request) -> Any:
    """Synchronously invoke the agent (runs in thread pool)."""
    agent = req.app.state.agent
    context = _build_context(request.context)
    input_data = _build_input(request.messages)

    result = await asyncio.to_thread(
        agent.invoke,
        input_data,
        config=request.config,
        context=context,
        **_default_agent_kwargs(),
    )
    return result


@router.post("/ainvoke")
async def agent_ainvoke(request: InvokeRequest, req: Request) -> Any:
    """Asynchronously invoke the agent."""
    agent = req.app.state.agent
    context = _build_context(request.context)
    input_data = _build_input(request.messages)

    result = await agent.ainvoke(
        input_data,
        config=request.config,
        context=context,
        **_default_agent_kwargs(),
    )
    return result


@router.post("/stream")
async def agent_stream(request: StreamRequest, req: Request) -> StreamingResponse:
    """Synchronously stream the agent response via SSE."""
    agent = req.app.state.agent
    context = _build_context(request.context)
    input_data = _build_input(request.messages)

    def event_generator():
        for chunk in agent.stream(
            input_data,
            config=request.config,
            context=context,
            **_default_agent_kwargs(),
        ):
            yield f"data: {json.dumps(chunk, default=str)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/astream")
async def agent_astream(request: StreamRequest, req: Request) -> StreamingResponse:
    """Asynchronously stream the agent response via SSE."""
    agent = req.app.state.agent
    context = _build_context(request.context)
    input_data = _build_input(request.messages)

    async def event_generator():
        async for chunk in agent.astream(
            input_data,
            config=request.config,
            context=context,
            **_default_agent_kwargs(),
        ):
            yield f"data: {json.dumps(chunk, default=str)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
