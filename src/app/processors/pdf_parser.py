"""
PyMuPDF4LLM PDF 解析器。

基于 PyMuPDF4LLM 的快速 PDF 文本提取。
"""

import os
import tempfile
from pathlib import Path

import pymupdf4llm

from app.core.config import settings


class PyMuPDF4LLMParser:
    """
    PyMuPDF4LLM PDF 解析器。

    使用 PyMuPDF4LLM 进行快速 PDF 文本提取，支持表格和图像。
    """

    def __init__(self):
        self.mode = settings.pdf_mode
        self.table_strategy = settings.pdf_table_strategy
        self.extract_images = settings.pdf_extract_images

    def parse_file(self, file_path: str) -> str:
        """
        解析本地 PDF 文件。

        Args:
            file_path: PDF 文件路径

        Returns:
            提取的文本内容（Markdown 格式）
        """
        return pymupdf4llm.to_markdown(
            file_path,
            page_chunks=False,
            write_images=self.extract_images,
            show_progress=False,
            table_strategy=self.table_strategy,
        )

    def parse_bytes(self, pdf_bytes: bytes) -> str:
        """
        解析 PDF 字节数据。

        Args:
            pdf_bytes: PDF 文件的字节内容

        Returns:
            提取的文本内容（Markdown 格式）
        """
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            return self.parse_file(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
