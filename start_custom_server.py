#!/usr/bin/env python3
"""
Custom LangGraph Server with configurable checkpointer and store.

Supports SQLite-backed persistence via AsyncSqliteSaver and AsyncSqliteStore.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

def setup_environment() -> None:
    """Ensure src/ is on PYTHONPATH and load .env if present."""
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
        except ImportError:
            pass


setup_environment()

from app.api import router  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize SQLite persistence and build agent."""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from langgraph.store.sqlite import AsyncSqliteStore
    from app.agents.agent import build_agent

    db_dir = Path(__file__).parent / "data"
    db_dir.mkdir(parents=True, exist_ok=True)


    try:
        async with AsyncSqliteSaver.from_conn_string(
            str(db_dir / "checkpoints.sqlite")
        ) as checkpointer:
            await checkpointer.setup()
            print("Checkpointer (SQLite) initialized")

            async with AsyncSqliteStore.from_conn_string(
                str(db_dir / "store.sqlite")
            ) as store:
                await store.setup()
                print("Store (SQLite) initialized")

                agent = await build_agent(checkpointer, store)
                app.state.agent = agent
                app.state.checkpointer = checkpointer
                app.state.store = store

                print(f"Agent loaded: {agent.name if hasattr(agent, 'name') else 'unnamed'}")
                yield

    except Exception as e:
        print(f"Initialization failed: {e}")
        raise RuntimeError(f"Server initialization failed: {e}") from e

    finally:
        print("Server shutting down...")


app = FastAPI(
    title="Custom LangGraph API",
    description="LangGraph API with SQLite persistence",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def main() -> None:
    """Start the Uvicorn server."""
    host = "0.0.0.0"
    port = 2026

    print("\n" + "=" * 60)
    print("Custom LangGraph Server")
    print("=" * 60)
    print(f"Server URL: http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/ok")
    print("=" * 60 + "\n")

    uvicorn.run(
        "start_custom_server:app",
        host=host,
        port=port,
        reload=False,
        access_log=True,
    )


if __name__ == "__main__":
    main()
