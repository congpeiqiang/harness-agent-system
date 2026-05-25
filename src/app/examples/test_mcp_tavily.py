"""@File    :   test_mcp_tavily.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   Tavily MCP 服务器测试脚本

Tavily MCP 服务器提供网络搜索功能。
文档: https://mcp.tavily.com/mcp/

使用方法:
    # 设置环境变量
    export TAVILY_API_KEY=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
    
    # 运行测试
    python -m app.examples.test_mcp_tavily
    
    # 使用自定义查询
    python -m app.examples.test_mcp_tavily --query "Python latest features"
    
    # 指定搜索选项
    python -m app.examples.test_mcp_tavily --query "AI news" --max-results 5 --search-depth advanced
"""

import asyncio
import argparse
import os
from typing import Optional

from dotenv import load_dotenv

from app.tools.mcp_client_builder import MCPClientBuilder
from app.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

# Tavily MCP 服务器配置
TAVILY_MCP_URL = "https://mcp.tavily.com/mcp/"


async def test_tavily_search(
    api_key: str,
    query: str = "What are the latest developments in AI?",
    max_results: int = 5,
    search_depth: str = "basic",
    include_images: bool = False,
    include_answer: bool = True,
):
    """测试 Tavily 搜索功能
    
    Args:
        api_key: Tavily API Key
        query: 搜索查询
        max_results: 最大返回结果数
        search_depth: 搜索深度 (basic 或 advanced)
        include_images: 是否包含图片
        include_answer: 是否包含 AI 生成的答案
    """
    logger.info("=== Tavily MCP 搜索测试 ===")
    logger.info(f"查询: {query}")
    logger.info(f"最大结果数: {max_results}")
    logger.info(f"搜索深度: {search_depth}")
    
    # 创建 MCP 客户端
    builder = MCPClientBuilder()
    
    # 添加 Tavily MCP 服务器（使用 URL 参数传递 API Key）
    tavily_url = f"{TAVILY_MCP_URL}?tavilyApiKey={api_key}"
    
    builder.add_http_server(
        name="tavily",
        url=tavily_url,
    )
    
    logger.info(f"连接到 Tavily MCP 服务器...")
    logger.info(f"URL: {TAVILY_MCP_URL}")
    
    client = await builder.create_client()
    # 获取可用工具
    tools = await client.get_tools()
    logger.info(f"可用工具: {[t.name for t in tools]}")

    return tools


async def test_tavily_raw_tools(api_key: str, query: str):
    """直接测试 Tavily 工具（不通过 Agent）"""
    logger.info("=== Tavily 工具直接调用测试 ===")
    
    from langchain_mcp_adapters.sessions import create_session
    from langchain_mcp_adapters.tools import load_mcp_tools
    
    # 创建连接配置
    connection = {
        "transport": "streamable_http",
        "url": f"{TAVILY_MCP_URL}?tavilyApiKey={api_key}",
    }
    
    logger.info(f"创建会话: {TAVILY_MCP_URL}")
    
    async with create_session(connection) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        
        logger.info(f"加载了 {len(tools)} 个工具")
        
        for tool in tools:
            logger.info(f"  - {tool.name}: {tool.description}")
        
        # 调用搜索工具
        if tools:
            search_tool = tools[0]  # 通常是 tavily_search
            logger.info(f"\n调用工具: {search_tool.name}")
            
            result = await search_tool.ainvoke({
                "query": query,
                "max_results": 3,
            })
            
            logger.info(f"结果: {result}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Tavily MCP Test")
    parser.add_argument(
        "--api-key",
        default=os.getenv("TAVILY_API_KEY"),
        help="Tavily API Key (默认从环境变量 TAVILY_API_KEY 读取)",
    )
    parser.add_argument(
        "--query",
        default="What are the latest developments in AI?",
        help="搜索查询",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="最大返回结果数 (默认: 5)",
    )
    parser.add_argument(
        "--search-depth",
        choices=["basic", "advanced"],
        default="basic",
        help="搜索深度 (默认: basic)",
    )
    parser.add_argument(
        "--mode",
        choices=["single", "multi", "raw", "all"],
        default="single",
        help="测试模式 (默认: single)",
    )
    
    args = parser.parse_args()
    
    if not args.api_key:
        logger.error("错误: 请提供 Tavily API Key")
        logger.error("可以通过 --api-key 参数或 TAVILY_API_KEY 环境变量提供")
        return
    
    logger.info(f"使用 API Key: {args.api_key[:20]}...")
    
    if args.mode in ("single", "all"):
        await test_tavily_search(
            api_key=args.api_key,
            query=args.query,
            max_results=args.max_results,
            search_depth=args.search_depth,
        )

if __name__ == "__main__":
    asyncio.run(main())
