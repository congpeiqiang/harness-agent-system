"""@File    :   mcp_server_math.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   MCP 数学运算服务器示例

使用方法:
    # 直接运行服务器 (stdio 模式)
    python -m app.mcp_server.mcp_server_math

    # SSE 模式
    python -m app.mcp_server.mcp_server_math --transport sse --port 8000

    # SSE 模式 + 自定义主机
    python -m app.mcp_server.mcp_server_math --transport sse --host 0.0.0.0 --port 8080

    # 启用调试日志
    python -m app.mcp_server.mcp_server_math --debug
"""

import os
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from app.logger import setup_logger

logger = setup_logger(__name__)


def create_math_server(
    name: str = "math",
    debug: bool = False,
    **kwargs: Any
) -> FastMCP:
    """创建数学运算 MCP 服务器
    
    Args:
        name: 服务器名称
        debug: 是否启用调试模式
        **kwargs: 传递给 FastMCP 的其他参数
        
    Returns:
        FastMCP 服务器实例
    """
    mcp = FastMCP(
        name=name,
        instructions="""Math MCP Server - Provides mathematical calculation tools.

Available tools:
- add: Add two numbers
- subtract: Subtract two numbers  
- multiply: Multiply two numbers
- divide: Divide two numbers
- power: Calculate power of a number
- sqrt: Calculate square root

All tools support both integers and floating-point numbers.
""",
        debug=debug,
        **kwargs
    )
    
    # 注册所有数学工具
    _register_math_tools(mcp)
    
    logger.info(f"Math MCP Server '{name}' created successfully")
    return mcp


def _register_math_tools(mcp: FastMCP) -> None:
    """注册数学运算工具"""

    @mcp.tool()
    async def add(a: float, b: float) -> float:
        """Add two numbers
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        logger.debug(f"add({a}, {b})")
        return a + b

    @mcp.tool()
    async def multiply(a: float, b: float) -> float:
        """Multiply two numbers
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        logger.debug(f"multiply({a}, {b})")
        return a * b

    @mcp.tool()
    def subtract(a: float, b: float) -> float:
        """Subtract two numbers
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference (a - b)
        """
        return a - b

    @mcp.tool()
    def divide(a: float, b: float) -> float:
        """Divide two numbers
        
        Args:
            a: Dividend
            b: Divisor
            
        Returns:
            Quotient (a / b)
            
        Raises:
            ValueError: If divisor is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    @mcp.tool()
    def power(base: float, exponent: float) -> float:
        """Calculate base raised to the power of exponent
        
        Args:
            base: Base number
            exponent: Exponent
            
        Returns:
            base ** exponent
        """
        return base ** exponent

    @mcp.tool()
    def sqrt(x: float) -> float:
        """Calculate the square root of a number
        
        Args:
            x: Input number (must be non-negative)
            
        Returns:
            Square root of x
            
        Raises:
            ValueError: If x is negative
        """
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return x ** 0.5

    @mcp.tool()
    def factorial(n: int) -> int:
        """Calculate factorial of n
        
        Args:
            n: Non-negative integer
            
        Returns:
            n!
            
        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @mcp.tool()
    def modulo(a: float, b: float) -> float:
        """Calculate modulo (remainder of division)
        
        Args:
            a: Dividend
            b: Divisor
            
        Returns:
            Remainder of a / b
            
        Raises:
            ValueError: If divisor is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a % b

    logger.info("Math tools registered successfully")


# 创建全局服务器实例
mcp = create_math_server()


async def run_sse_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    mount_path: Optional[str] = None,
) -> None:
    """运行 SSE 模式的服务器
    
    Args:
        host: 主机地址
        port: 端口号
        mount_path: 挂载路径（可选）
    """
    logger.info(f"Starting SSE server on http://{host}:{port}")
    if mount_path:
        logger.info(f"Mount path: {mount_path}")
    await mcp.run_sse_async(mount_path=mount_path)


def main():
    """主函数"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Math MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address for SSE mode (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE mode (default: 8000)",
    )
    parser.add_argument(
        "--mount-path",
        default=None,
        help="Mount path for SSE mode (optional)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")

    if args.transport == "stdio":
        logger.info("Starting stdio server...")
        mcp.run()
    elif args.transport == "sse":
        logger.info(f"Starting SSE server on http://{args.host}:{args.port}")
        asyncio.run(run_sse_server(
            host=args.host,
            port=args.port,
            mount_path=args.mount_path,
        ))


if __name__ == "__main__":
    main()
