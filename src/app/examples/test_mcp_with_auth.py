"""@File    :   test_mcp_with_auth.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   MCP 带认证测试脚本

使用方法:
    # 测试 Token 认证
    python -m app.examples.test_mcp_with_auth --token YOUR_JWT_TOKEN
    
    # 使用自定义认证类型
    python -m app.examples.test_mcp_with_auth --token YOUR_API_KEY --auth-type ApiKey
    
    # 使用自定义 headers
    python -m app.examples.test_mcp_with_auth --headers "Authorization:Bearer xxx,X-Custom:value"
"""

import asyncio
import argparse
from typing import Optional, Dict

from app.tools.mcp_client_builder import MCPClientBuilder, create_mcp_agent
from app.logger import setup_logger

logger = setup_logger(__name__)


def parse_headers(header_str: Optional[str]) -> Optional[Dict[str, str]]:
    """解析 headers 字符串
    
    Args:
        header_str: headers 字符串，格式: "key1:value1,key2:value2"
        
    Returns:
        headers 字典
    """
    if not header_str:
        return None
    
    headers = {}
    pairs = header_str.split(",")
    for pair in pairs:
        if ":" in pair:
            key, value = pair.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers


async def test_bearer_token(url: str, token: str):
    """测试 Bearer Token 认证"""
    logger.info(f"=== 测试 Bearer Token 认证 ===")
    logger.info(f"URL: {url}")
    logger.info(f"Token: {token[:10]}...")
    
    builder = MCPClientBuilder()
    builder.add_http_server(
        name="api",
        url=url,
        token=token,
        auth_type="Bearer",
    )
    
    # 验证配置
    config = builder.get_server_config("api")
    logger.info(f"Authorization Header: {config.get('headers', {}).get('Authorization', 'None')}")
    
    try:
        client = await builder.create_client()
        async with client:
            tools = await client.get_tools()
            logger.info(f"连接成功！可用工具: {[t.name for t in tools]}")
    except Exception as e:
        logger.error(f"连接失败: {e}")


async def test_custom_auth(url: str, token: str, auth_type: str):
    """测试自定义认证类型"""
    logger.info(f"=== 测试 {auth_type} 认证 ===")
    
    builder = MCPClientBuilder()
    builder.add_http_server(
        name="api",
        url=url,
        token=token,
        auth_type=auth_type,
    )
    
    config = builder.get_server_config("api")
    auth_header = config.get('headers', {}).get('Authorization', 'None')
    logger.info(f"Authorization Header: {auth_header}")


async def test_custom_headers(url: str, headers: Dict[str, str]):
    """测试自定义 Headers"""
    logger.info(f"=== 测试自定义 Headers ===")
    logger.info(f"Headers: {headers}")
    
    builder = MCPClientBuilder()
    builder.add_http_server(
        name="api",
        url=url,
        headers=headers,
    )
    
    config = builder.get_server_config("api")
    logger.info(f"配置中的 Headers: {config.get('headers', {})}")


async def test_add_server_with_token(url: str, token: str):
    """测试 add_server_with_token 便捷方法"""
    logger.info(f"=== 测试 add_server_with_token 便捷方法 ===")
    
    builder = MCPClientBuilder()
    builder.add_server_with_token(
        name="api",
        url=url,
        token=token,
    )
    
    config = builder.get_server_config("api")
    auth_header = config.get('headers', {}).get('Authorization', 'None')
    logger.info(f"Authorization Header: {auth_header}")
    logger.info(f"服务器列表: {builder.list_servers()}")


async def test_token_with_other_headers(url: str, token: str):
    """测试 Token 与其他 Headers 共存"""
    logger.info(f"=== 测试 Token 与其他 Headers 共存 ===")
    
    builder = MCPClientBuilder()
    builder.add_http_server(
        name="api",
        url=url,
        token=token,
        headers={
            "X-Custom-Header": "custom-value",
            "X-Request-ID": "12345",
        }
    )
    
    config = builder.get_server_config("api")
    logger.info(f"所有 Headers: {config.get('headers', {})}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MCP Auth Test")
    parser.add_argument(
        "--url",
        default="http://localhost:8000/mcp",
        help="MCP 服务器 URL",
    )
    parser.add_argument(
        "--token",
        default="test-token-12345",
        help="身份验证 Token",
    )
    parser.add_argument(
        "--auth-type",
        default="Bearer",
        help="认证类型 (默认: Bearer)",
    )
    parser.add_argument(
        "--headers",
        default=None,
        help="自定义 Headers，格式: key1:value1,key2:value2",
    )
    parser.add_argument(
        "--test",
        choices=["bearer", "custom", "headers", "convenience", "combined", "all"],
        default="all",
        help="测试类型",
    )
    
    args = parser.parse_args()
    
    if args.test in ("bearer", "all"):
        await test_bearer_token(args.url, args.token)
        print()
    
    if args.test in ("custom", "all"):
        await test_custom_auth(args.url, args.token, args.auth_type)
        print()
    
    if args.test in ("headers", "all"):
        custom_headers = parse_headers(args.headers) or {
            "Authorization": "Bearer custom-token",
            "X-Custom": "value"
        }
        await test_custom_headers(args.url, custom_headers)
        print()
    
    if args.test in ("convenience", "all"):
        await test_add_server_with_token(args.url, args.token)
        print()
    
    if args.test in ("combined", "all"):
        await test_token_with_other_headers(args.url, args.token)


if __name__ == "__main__":
    asyncio.run(main())
