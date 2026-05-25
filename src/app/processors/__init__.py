"""
@File    :   __init__.py
@Author  :   CongPeiQiang
@Time    :   2026/5/22 10:48
@Desc    :   处理器模块，提供 PDF 解析等功能
"""

from app.processors.pdf_parser import PDFParser, _compute_file_hash, _compute_bytes_hash, _decode_content, _do_parse_pdf_from_file
from app.processors.docling_pdf_parser import (
    DoclingPDFParser,
    _compute_file_hash as _docling_compute_file_hash,
    _compute_bytes_hash as _docling_compute_bytes_hash,
    _decode_content as _docling_decode_content,
    _do_parse_pdf_from_file as _docling_do_parse_pdf_from_file,
)

__all__ = [
    "PDFParser",
    "DoclingPDFParser",
    "_compute_file_hash",
    "_compute_bytes_hash",
    "_decode_content",
    "_do_parse_pdf_from_file",
]
