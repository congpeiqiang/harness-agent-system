"""
@File    :  mcp_server_client.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:57
@Desc    :  
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FecMallClient:
    def __init__(self, config: FecMallConfig):
        """
        初始化FecMall客户端
        Args:
            config: FecMall配置对象
        """
        self.config = config
        self.mcp_client = MultiServerMCPClient(
            {
                "fecmall-mcp": {
                    "url": self.config.get_setting('mcp_url', 'http://127.0.0.1:8000/sse'),
                    "transport": self.config.get_setting('mcp_transport', 'sse'),
                }
            }
        )
        self._tool_map = {}
        self._initialized = False

    async def initialize(self) -> None:
        """
        初始化客户端，获取工具列表
        """
        if not self._initialized:
            self.tools = await self.mcp_client.get_tools()
            self._tool_map = {tool.name: tool for tool in self.tools}
            self._initialized = True

    async def get_tools(self) -> list:
        """
        获取所有可用的工具
        Returns:
            list: 工具列表
        """
        if not self._initialized:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(self.initialize())
            else:
                raise RuntimeError("Cannot get tools in a running event loop")
        return self.tools

    def get_tool_by_name(self, name: str) -> Optional[Any]:
        """
        根据名称获取工具
        Args:
            name: 工具名称
        Returns:
            Optional[Any]: 工具对象或None
        """
        if not self._initialized:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(self.initialize())
            else:
                raise RuntimeError("Cannot get tools in a running event loop")
        return self._tool_map.get(name)

# 示例使用
async def mcp_tools():
    """示例使用方法"""
    # 初始化配置和客户端
    config = FecMallConfig()
    client = FecMallClient(config)
    try:
        # 初始化客户端
        await client.initialize()
        return await client.get_tools()
    finally:
        # 关闭连接
        pass


tools = asyncio.run(mcp_tools())
