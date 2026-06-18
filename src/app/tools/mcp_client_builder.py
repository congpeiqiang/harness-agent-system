"""
FecMall MCP 客户端构建器模块。

负责管理 FecMall 电商平台的 MCP 服务器连接和工具获取。
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Any


async def get_mcp_tools_async() -> list[Any]:
    """
    异步获取 FecMall MCP 工具列表。

    尝试连接 FecMall MCP 服务器，如果失败则返回空列表。
    """
    try:
        from langchain_mcp_adapters.tools import load_mcp_tools

        project_root = Path(__file__).parent.parent.parent.parent
        fecmall_dir = project_root / "fecmall_check"
        server_script = fecmall_dir / "mcp_server.py"

        if not server_script.exists():
            return []

        import httpx

        port = 21111
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"http://localhost:{port}/health", timeout=2.0)
                if resp.status_code == 200:
                    from mcp import ClientSession, StdioServerParameters
                    from mcp.client.stdio import stdio_client

                    server_params = StdioServerParameters(
                        command="python",
                        args=[str(server_script)],
                        cwd=str(fecmall_dir),
                    )

                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            tools = await load_mcp_tools(session)
                            return tools
            except (httpx.ConnectError, httpx.TimeoutException):
                pass

        return []
    except Exception as e:
        print(f"[警告] FecMall MCP 工具加载失败: {e}")
        return []
