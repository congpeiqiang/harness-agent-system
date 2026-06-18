"""
PDF 工具测试。

测试 PDF 解析工具的功能。
"""

import pytest
from pathlib import Path
from app.tools.pdf_tool import parse_pdf_from_file, parse_pdf_from_content, parse_pdf_from_url


class TestPDFTool:
    """PDF 工具测试。"""

    def test_parse_pdf_from_file_not_exists(self):
        """测试解析不存在的文件。"""
        result = parse_pdf_from_file.invoke({"path": "nonexistent.pdf"})
        assert "错误" in result or "失败" in result

    def test_parse_pdf_from_file_not_pdf(self):
        """测试解析非 PDF 文件。"""
        result = parse_pdf_from_file.invoke({"path": "README.md"})
        assert "错误" in result or "失败" in result

    def test_parse_pdf_from_content_invalid(self):
        """测试解析无效的 Base64 内容。"""
        result = parse_pdf_from_content.invoke({"content": "invalid_base64"})
        assert "失败" in result or "错误" in result

    def test_parse_pdf_from_url_invalid(self):
        """测试从无效 URL 下载 PDF。"""
        result = parse_pdf_from_url.invoke({"url": "https://invalid.example.com/test.pdf"})
        assert "失败" in result or "错误" in result
