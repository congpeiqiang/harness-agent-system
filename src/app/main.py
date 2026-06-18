"""
LangGraph Agent API - 应用入口。

提供 FastAPI 应用，包含健康检查、指标和 Agent API 端点。
"""

import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 确保 src/ 在 PYTHONPATH 中
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from app.core.config import settings
from app.api import router as agent_router


# ---------------------------------------------------------------------------
# 生命周期：初始化持久化层并构建 Agent
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：初始化 SQLite 持久化并构建 Agent。"""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from langgraph.store.sqlite import AsyncSqliteStore
    from app.agents.agent import build_agent

    db_dir = Path(__file__).parent.parent.parent / "data"
    db_dir.mkdir(parents=True, exist_ok=True)

    try:
        async with AsyncSqliteSaver.from_conn_string(
            str(db_dir / "checkpoints.sqlite")
        ) as checkpointer:
            await checkpointer.setup()
            print("[初始化] 检查点 (SQLite) 已就绪")

            async with AsyncSqliteStore.from_conn_string(
                str(db_dir / "store.sqlite")
            ) as store:
                await store.setup()
                print("[初始化] 存储 (SQLite) 已就绪")

                agent = await build_agent(checkpointer, store)
                app.state.agent = agent
                app.state.checkpointer = checkpointer
                app.state.store = store
                app.state.start_time = time.time()

                agent_name = getattr(agent, "name", "未命名")
                print(f"[初始化] Agent 已加载: {agent_name}")
                yield

    except Exception as e:
        print(f"[错误] 初始化失败: {e}")
        raise RuntimeError(f"服务器初始化失败: {e}") from e
    finally:
        print("[初始化] 服务器正在关闭...")


# ---------------------------------------------------------------------------
# FastAPI 应用
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Harness Agent System API",
    description="基于 LangGraph 和 MCP 的智能 Agent 系统",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS 配置 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- 速率限制（可选）---
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": f"超过速率限制: {exc.detail}"},
        )
except ImportError:
    limiter = None

# --- 路由注册 ---
app.include_router(agent_router, prefix="/agent")


# ---------------------------------------------------------------------------
# 健康检查与指标端点
# ---------------------------------------------------------------------------

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点，用于容器编排。"""
    uptime = time.time() - getattr(app.state, "start_time", time.time())
    return {
        "status": "healthy",
        "version": "0.1.0",
        "uptime_seconds": round(uptime, 2),
    }


@app.get("/ok", tags=["健康检查"])
async def ok():
    """简单存活探针。"""
    return {"status": "ok"}


@app.get("/metrics", tags=["监控"])
async def metrics():
    """基础指标端点。"""
    uptime = time.time() - getattr(app.state, "start_time", time.time())
    return {
        "uptime_seconds": round(uptime, 2),
        "version": "0.1.0",
    }
