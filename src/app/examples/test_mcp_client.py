"""@File    :   test_mcp_client.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   MCP 客户端测试脚本

使用方法:
    # 测试 stdio 服务器
    python -m app.examples.test_mcp_client --mode stdio
    
    # 测试带 Token 的 HTTP 服务器
    python -m app.examples.test_mcp_client --mode http --token YOUR_TOKEN
    
    # 指定服务器 URL
    python -m app.examples.test_mcp_client --mode http --url http://localhost:8000/mcp
"""

import asyncio
import argparse
from typing import Optional

from app.tools.mcp_client_builder import (
    MCPClientBuilder,
    create_mcp_agent,
    quick_mcp_agent,
)
from app.logger import setup_logger

logger = setup_logger(__name__)


async def test_stdio_server():
    """测试 stdio 模式的 MCP 服务器"""
    logger.info("=== 测试 stdio 服务器 ===")
    
    builder = MCPClientBuilder()
    builder.add_stdio_server(
        name="math",
        command="python",
        args=["-m", "app.mcp_server.mcp_server_math"]
    )
    
    client = await builder.create_client()
    async with client:
        tools = await client.get_tools()
        logger.info(f"可用工具: {[t.name for t in tools]}")
        
        # 创建 Agent
        agent = create_mcp_agent("deepseek-chat", tools)
        
        # 测试计算
        queries = [
            "what is 3 plus 5?",
            "what is 10 multiplied by 12?",
            "what is (3 + 5) x 12?",
        ]
        
        for query in queries:
            logger.info(f"\n查询: {query}")
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": query}]
            })
            logger.info(f"结果: {result}")


async def test_http_server(url: str, token: Optional[str] = None):
    """测试 HTTP 模式的 MCP 服务器
    
    Args:
        url: MCP 服务器 URL
        token: 可选的身份验证令牌
    """
    logger.info(f"=== 测试 HTTP 服务器: {url} ===")
    
    builder = MCPClientBuilder()
    
    if token:
        # 使用 Token 认证
        builder.add_http_server(
            name="weather",
            url=url,
            token=token,
        )
        logger.info("使用 Token 认证")
    else:
        # 无认证
        builder.add_http_server(
            name="weather",
            url=url,
        )
    
    client = await builder.create_client()
    async with client:
        tools = await client.get_tools()
        logger.info(f"可用工具: {[t.name for t in tools]}")
        
        # 创建 Agent
        agent = create_mcp_agent("deepseek-chat", tools)
        
        # 测试查询
        query = "what is the weather in New York?"
        logger.info(f"\n查询: {query}")
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": query}]
        })
        logger.info(f"结果: {result}")


async def test_quick_agent():
    """测试快速 MCP Agent 功能"""
    logger.info("=== 测试 quick_mcp_agent ===")
    
    server_config = {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "app.mcp_server.mcp_server_math"],
        }
    }
    
    result = await quick_mcp_agent(
        query="what is 100 divided by 4?",
        server_config=server_config,
        model="deepseek-chat",
    )
    
    logger.info(f"结果: {result}")


async def test_multi_server():
    """测试多个 MCP 服务器"""
    logger.info("=== 测试多个 MCP 服务器 ===")
    
    builder = MCPClientBuilder()
    
    # 添加数学服务器
    builder.add_stdio_server(
        name="math",
        command="python",
        args=["-m", "app.mcp_server.mcp_server_math"]
    )
    
    # 添加另一个服务器（示例）
    # builder.add_http_server(
    #     name="weather",
    #     url="http://localhost:8000/mcp",
    # )
    
    client = await builder.create_client()
    async with client:
        tools = await client.get_tools()
        logger.info(f"可用工具总数: {len(tools)}")
        logger.info(f"工具列表: {[t.name for t in tools]}")


async def test_builder_chain():
    """测试构建器链式调用"""
    logger.info("=== 测试构建器链式调用 ===")
    
    tools = await (
        MCPClientBuilder()
        .add_stdio_server(
            name="math",
            command="python",
            args=["-m", "app.mcp_server.mcp_server_math"]
        )
        .create_client()
    ).get_tools()
    
    logger.info(f"链式调用成功，可用工具: {[t.name for t in tools]}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MCP Client Test")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http", "quick", "multi", "chain", "all"],
        default="stdio",
        help="测试模式 (默认: stdio)",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/mcp",
        help="HTTP 服务器 URL (默认: http://localhost:8000/mcp)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="身份验证 Token",
    )
    
    args = parser.parse_args()
    
    if args.mode == "stdio" or args.mode == "all":
        await test_stdio_server()
    
    if args.mode == "http" or args.mode == "all":
        await test_http_server(args.url, args.token)
    
    if args.mode == "quick" or args.mode == "all":
        await test_quick_agent()
    
    if args.mode == "multi" or args.mode == "all":
        await test_multi_server()
    
    if args.mode == "chain" or args.mode == "all":
        await test_builder_chain()


if __name__ == "__main__":
    asyncio.run(main())
