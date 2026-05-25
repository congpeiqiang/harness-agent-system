"""
@File    :   __init__.py
@Author  :   CongPeiQiang
@Time    :   2026/5/22 10:48
@Desc    :   处理器模块，提供 PDF 解析等功能
"""

from app.processors.pdf_parser import PDFParser, _do_parse_pdf_from_file
from app.processors.docling_pdf_parser import DoclingPDFParser, _do_parse_pdf_from_file as _docling_do_parse_pdf_from_file
from app.processors.pdf_cache import (
    PDFCacheManager,
    SharedCache,
    get_cache_manager,
    compute_file_hash,
    compute_bytes_hash,
    decode_content,
)

__all__ = [
    "PDFParser",
    "DoclingPDFParser",
    "PDFCacheManager",
    "SharedCache",
    "get_cache_manager",
    "compute_file_hash",
    "compute_bytes_hash",
    "decode_content",
    "_do_parse_pdf_from_file",
    "_docling_do_parse_pdf_from_file",
]
