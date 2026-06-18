"""
PDF 解析器模块。

提供 PyMuPDF4LLM 和 Docling 两种 PDF 解析器。
"""

from app.processors.pdf_parser import PyMuPDF4LLMParser, DoclingParser

__all__ = ["PyMuPDF4LLMParser", "DoclingParser"]
