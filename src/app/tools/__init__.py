"""
@File    :  __init__.py
@Author  :  CongPeiQiang
@Time    :  2026/5/22 14:05
@Desc    :  工具模块，提供 PDF 解析等功能
"""
from app.tools.pdf_parse_tool import (
    parse_pdf_from_file,
    parse_pdf_from_content,
    parse_pdf_from_url,
    clear_pdf_cache,
    get_cache_stats,
)

# MCP 相关工具
from app.tools.mcp_client_builder import (
    MCPClientBuilder,
    create_mcp_agent,
    quick_mcp_agent,
    create_pdf_mcp_client,
)

__all__ = [
    # PDF 工具
    "parse_pdf_from_file",
    "parse_pdf_from_content",
    "parse_pdf_from_url",
    "clear_pdf_cache",
    "get_cache_stats",
    # MCP 工具
    "MCPClientBuilder",
    "create_mcp_agent",
    "quick_mcp_agent",
    "create_pdf_mcp_client",
]
