#!/usr/bin/env python3
"""
Custom LangGraph Server with configurable checkpointer and store

支持自定义 checkpointer 和 store 的启动脚本
"""

import os
import sys
import json
from pathlib import Path
from contextlib import asynccontextmanager

# 设置环境变量
def setup_environment():
    """Setup required environment variables"""
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Load .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ Loaded environment from .env")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env file")

# 提前设置环境变量
setup_environment()

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import AsyncIterator, Dict, Any, Optional
import asyncio

# 导入 agent（这会初始化带自定义 checkpointer/store 的 agent）
from app.agents.agent import agent

# 导入自定义的 checkpointer 和 store（需要在 agent.py 中导出）
try:
    from app.agents.agent import checkpointer, store
    print(f"✅ Loaded custom checkpointer: {type(checkpointer).__name__}")
    print(f"✅ Loaded custom store: {type(store).__name__ if store else 'None'}")
except ImportError:
    print("⚠️  Using default checkpointer/store from agent")
    checkpointer = None
    store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 Starting Custom LangGraph Server...")
    print(f"📍 Agent loaded: {agent.name if hasattr(agent, 'name') else 'unnamed'}")
    yield
    print("🛑 Server shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Custom LangGraph API",
    description="LangGraph API with custom checkpointer and store",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径 - 服务信息"""
    return {
        "message": "Custom LangGraph API Server",
        "docs": "/docs",
        "endpoints": {
            "invoke": "/invoke",
            "stream": "/stream",
            "batch": "/batch",
        }
    }


@app.get("/health")
@app.get("/ok")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "checkpointer": type(checkpointer).__name__ if checkpointer else "default",
        "store": type(store).__name__ if store else "default"
    }


@app.post("/invoke")
async def invoke(request: Dict[str, Any]):
    """
    同步调用 agent
    
    请求体:
    {
        "messages": [{"role": "user", "content": "..."}],
        "config": {"configurable": {"thread_id": "..."}}
    }
    """
    try:
        messages = request.get("messages", [])
        config = request.get("config", {})
        
        # 调用 agent
        result = await agent.ainvoke(
            {"messages": messages},
            config=config
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
async def stream(request: Dict[str, Any]):
    """
    流式调用 agent
    
    请求体:
    {
        "messages": [{"role": "user", "content": "..."}],
        "config": {"configurable": {"thread_id": "..."}}
    }
    """
    try:
        messages = request.get("messages", [])
        config = request.get("config", {})
        
        async def event_stream() -> AsyncIterator[str]:
            async for chunk in agent.astream(
                {"messages": messages},
                config=config
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch")
async def batch(request: Dict[str, Any]):
    """
    批量调用 agent
    
    请求体:
    {
        "inputs": [
            {"messages": [{"role": "user", "content": "..."}]},
            ...
        ],
        "config": {"configurable": {"thread_id": "..."}}
    }
    """
    try:
        inputs = request.get("inputs", [])
        config = request.get("config", {})
        
        results = await agent.abatch(
            [{"messages": inp.get("messages", [])} for inp in inputs],
            config=config
        )
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """获取指定线程的状态"""
    try:
        if checkpointer:
            config = {"configurable": {"thread_id": thread_id}}
            state = await checkpointer.aget(config)
            return {
                "thread_id": thread_id,
                "state": state
            }
        else:
            return {
                "thread_id": thread_id,
                "state": None,
                "message": "No custom checkpointer available"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threads/{thread_id}/state")
async def update_thread_state(thread_id: str, update: Dict[str, Any]):
    """更新指定线程的状态"""
    try:
        if checkpointer:
            config = {"configurable": {"thread_id": thread_id}}
            await checkpointer.aput(config, update)
            return {
                "thread_id": thread_id,
                "status": "updated"
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail="No custom checkpointer available"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Start the server"""
    print("\n" + "="*60)
    print("🔧 Custom LangGraph Server")
    print("="*60)
    print(f"📍 Server URL: http://localhost:2026")
    print(f"📚 API Documentation: http://localhost:2026/docs")
    print(f"💚 Health Check: http://localhost:2026/ok")
    print("="*60 + "\n")
    
    uvicorn.run(
        "start_custom_server:app",
        host="0.0.0.0",
        port=2026,
        reload=False,
        access_log=True
    )


if __name__ == "__main__":
    main()
