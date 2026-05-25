"""@File    :   mcp_client_builder.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   MCP 客户端构建器，支持多服务器配置

使用方法:
    # 使用示例
    from app.tools.mcp_client_builder import MCPClientBuilder, create_mcp_agent
    
    # 方法1: 使用构建器模式
    builder = MCPClientBuilder()
    
    # 添加 stdio 服务器
    builder.add_stdio_server(
        name="math",
        command="python",
        args=["-m", "app.mcp_server.mcp_server_math"]
    )
    
    # 添加 HTTP/SSE 服务器（带 Token 认证）
    builder.add_http_server(
        name="weather",
        url="http://localhost:8000/mcp",
        token="YOUR_JWT_TOKEN"  # 自动添加 Authorization: Bearer YOUR_JWT_TOKEN
    )
    
    # 或使用自定义 headers
    builder.add_http_server(
        name="weather",
        url="http://localhost:8000/mcp",
        headers={
            "Authorization": "Bearer YOUR_TOKEN",
            "X-Custom-Header": "custom-value"
        }
    )
    
    # 获取工具并创建 Agent
    async with builder.create_client() as client:
        tools = await client.get_tools()
        agent = create_mcp_agent("deepseek-chat", tools)
        
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "what is 1 plus 1?"}]
        })
        print(response)
    
    # 方法2: 便捷方法 - 使用 Token
    builder.add_server_with_token(
        name="weather",
        url="http://localhost:8000/mcp",
        token="YOUR_JWT_TOKEN"
    )
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.core.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)


class MCPClientBuilder:
    """MCP 客户端构建器
    
    用于配置和管理多个 MCP 服务器连接，支持 stdio 和 HTTP/SSE 传输模式。
    """
    
    def __init__(self):
        """初始化 MCP 客户端构建器"""
        self._servers: Dict[str, Dict[str, Any]] = {}
    
    def add_stdio_server(
        self,
        name: str,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        encoding: str = "utf-8",
    ) -> MCPClientBuilder:
        """添加 stdio 传输模式的 MCP 服务器"""
        self._servers[name] = {
            "transport": "stdio",
            "command": command,
            "args": args or [],
            "env": env,
            "encoding": encoding,
        }
        logger.info(f"已添加 stdio 服务器: {name}")
        return self
    
    def add_http_server(
        self,
        name: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None,
        auth_type: str = "Bearer",
        **kwargs: Any,
    ) -> MCPClientBuilder:
        """添加 HTTP/SSE 传输模式的 MCP 服务器
        
        Args:
            name: 服务器名称
            url: 服务器 URL
            headers: 自定义 HTTP 请求头
            token: 身份验证令牌 (JWT/ApiKey)，将自动添加到 Authorization 头
            auth_type: 认证类型，默认为 "Bearer"，可为 "Bearer"、"Basic" 等
            **kwargs: 其他连接参数
            
        Returns:
            MCPClientBuilder 实例
            
        Example:
            # 使用 Token 认证
            builder.add_http_server(
                name="weather",
                url="http://localhost:8000/mcp",
                token="YOUR_JWT_TOKEN"
            )
            
            # 自定义请求头
            builder.add_http_server(
                name="weather",
                url="http://localhost:8000/mcp",
                headers={
                    "Authorization": "Bearer YOUR_TOKEN",
                    "X-Custom-Header": "custom-value"
                }
            )
        """
        server_config: Dict[str, Any] = {
            "transport": "streamable_http",
            "url": url,
        }
        
        # 处理 headers
        if headers:
            server_config["headers"] = headers.copy()
        else:
            server_config["headers"] = {}
        
        # 如果提供了 token，添加到 Authorization 头
        if token:
            server_config["headers"]["Authorization"] = f"{auth_type} {token}"
        
        # 合并其他参数
        server_config.update(kwargs)
        
        self._servers[name] = server_config
        logger.info(f"已添加 HTTP 服务器: {name} -> {url}")
        return self
    
    def add_server_with_token(
        self,
        name: str,
        url: str,
        token: str,
        auth_type: str = "Bearer",
        **kwargs: Any,
    ) -> MCPClientBuilder:
        """添加带 Token 认证的 MCP 服务器（便捷方法）
        
        Args:
            name: 服务器名称
            url: 服务器 URL
            token: 身份验证令牌
            auth_type: 认证类型，默认为 "Bearer"
            **kwargs: 其他连接参数
            
        Returns:
            MCPClientBuilder 实例
            
        Example:
            builder.add_server_with_token(
                name="weather",
                url="http://localhost:8000/mcp",
                token="YOUR_JWT_TOKEN"
            )
        """
        return self.add_http_server(
            name=name,
            url=url,
            token=token,
            auth_type=auth_type,
            **kwargs
        )
    
    def remove_server(self, name: str) -> MCPClientBuilder:
        """移除已配置的服务器"""
        if name in self._servers:
            del self._servers[name]
            logger.info(f"已移除服务器: {name}")
        return self
    
    def get_server_config(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定服务器的配置"""
        return self._servers.get(name)
    
    def list_servers(self) -> List[str]:
        """获取所有已配置的服务器名称列表"""
        return list(self._servers.keys())
    
    def clear_servers(self) -> MCPClientBuilder:
        """清除所有服务器配置"""
        self._servers.clear()
        logger.info("已清除所有服务器配置")
        return self
    
    async def create_client(self) -> MultiServerMCPClient:
        """创建多服务器 MCP 客户端"""
        if not self._servers:
            raise ValueError("没有配置任何 MCP 服务器")
        
        logger.info(f"创建 MCP 客户端，连接服务器: {list(self._servers.keys())}")
        return MultiServerMCPClient(self._servers)
    
    @classmethod
    def from_config(cls, config: Dict[str, Dict[str, Any]]) -> MCPClientBuilder:
        """从配置字典创建构建器"""
        builder = cls()
        builder._servers = config.copy()
        logger.info(f"从配置创建 MCP 客户端，服务器: {list(config.keys())}")
        return builder


# 便捷函数：创建 PDF MCP 客户端
async def create_pdf_mcp_client(
    transport: str = "stdio",
    host: str = "localhost",
    port: int = 8080,
    token: Optional[str] = None,
) -> MCPClientBuilder:
    """创建 PDF MCP 客户端构建器
    
    Args:
        transport: 传输模式，"stdio" 或 "sse"
        host: SSE 模式下的主机地址
        port: SSE 模式下的端口号
        token: 可选的身份验证令牌（仅 SSE 模式）
        
    Returns:
        MCPClientBuilder 实例
    """
    builder = MCPClientBuilder()
    
    if transport == "stdio":
        builder.add_stdio_server(
            name="pdf",
            command="python",
            args=["-m", "app.tools.mcp_builder"],
        )
    elif transport == "sse":
        if token:
            builder.add_http_server(
                name="pdf",
                url=f"http://{host}:{port}/mcp",
                token=token,
            )
        else:
            builder.add_http_server(
                name="pdf",
                url=f"http://{host}:{port}/mcp",
            )
    else:
        raise ValueError(f"不支持的传输模式: {transport}")
    
    return builder


if __name__ == "__main__":
    """测试示例"""
    
    async def test():
        """测试 MCP 客户端构建器"""
        # 使用构建器模式
        builder = MCPClientBuilder()
        builder.add_stdio_server(
            name="math",
            command="python",
            args=["-m", "app.mcp_server.mcp_server_math"]
        )
        
        client = await builder.create_client()
        async with client:
            tools = await client.get_tools()
            print(f"可用工具: {[t.name for t in tools]}")
            
            # 创建 Agent
            agent = create_mcp_agent("deepseek-chat", tools)
            
            # 测试计算
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": "what is 1 plus 1?"}]
            })
            print(f"Result: {result}")
    
    # 运行测试
    asyncio.run(test())
