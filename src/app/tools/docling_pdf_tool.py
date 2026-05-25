"""
@File    :  docling_pdf_tool.py
@Author  :  CodeGeeX
@Time    :  2026/5/25
@Desc    :  基于 Docling 的 PDF 解析工具
"""
import tempfile

from langchain.tools import tool

from app.processors.docling_pdf_parser import (
    DoclingPDFParser,
    _compute_file_hash,
    _compute_bytes_hash,
    _decode_content,
    _do_parse_pdf_from_file,
)
from app.core.config import settings
from app.logger import setup_logger

# 获取日志记录器
logger = setup_logger(__name__)

# 模块级共享 DoclingPDFParser 实例，供 @tool 函数使用缓存
_shared_parser = DoclingPDFParser()


@tool
def parse_pdf_from_file_docling(file_path: str) -> str:
    """使用 Docling 从文件路径解析 PDF，返回解析后的纯文本内容。

    解析配置（export_type、enable_multimodal 等）从 settings 自动读取。
    同一文件（基于内容哈希判断）不会重复解析，直接返回缓存结果。

    Args:
        file_path: PDF 文件绝对路径

    Returns:
        解析后的纯文本内容
    """
    file_hash = _compute_file_hash(file_path)

    # 命中缓存
    if file_hash in _shared_parser._cache:
        logger.info("命中缓存，跳过解析 | 文件: %s | 哈希: %s", file_path, file_hash[:12])
        docs = _shared_parser._cache[file_hash]
    else:
        docs = _do_parse_pdf_from_file(
            file_path,
            export_type=getattr(settings, "docling_export_type", "markdown"),
            enable_multimodal=settings.enable_pdf_multimodal,
            extract_images=settings.pdf_extract_images,
        )
        _shared_parser._evict_if_needed()
        _shared_parser._cache[file_hash] = docs
        logger.info("解析完成并缓存 | 文件: %s | 哈希: %s | 片段数: %d", file_path, file_hash[:12], len(docs))

    return "\n\n".join(doc.page_content for doc in docs)


@tool
def parse_pdf_from_content_docling(content: str) -> str:
    """使用 Docling 从 base64 编码内容解析 PDF，返回解析后的纯文本内容。

    解析配置（export_type、enable_multimodal 等）从 settings 自动读取。
    同一内容（基于哈希判断）不会重复解析，直接返回缓存结果。

    Args:
        content: base64 编码的 PDF 内容字符串

    Returns:
        解析后的纯文本内容
    """
    pdf_bytes = _decode_content(content)
    content_hash = _compute_bytes_hash(pdf_bytes)

    # 命中缓存
    if content_hash in _shared_parser._cache:
        logger.info("命中缓存，跳过解析 | 哈希: %s", content_hash[:12])
        docs = _shared_parser._cache[content_hash]
    else:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            docs = _do_parse_pdf_from_file(
                tmp_path,
                export_type=getattr(settings, "docling_export_type", "markdown"),
                enable_multimodal=settings.enable_pdf_multimodal,
                extract_images=settings.pdf_extract_images,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                import os
                os.remove(tmp_path)
                logger.debug("已清理临时文件: %s", tmp_path)

        _shared_parser._evict_if_needed()
        _shared_parser._cache[content_hash] = docs
        logger.info("解析完成并缓存 | 哈希: %s | 片段数: %d", content_hash[:12], len(docs))

    return "\n\n".join(doc.page_content for doc in docs)


@tool
def parse_pdf_with_docling_markdown(file_path: str) -> str:
    """使用 Docling 解析 PDF，返回 Markdown 格式的内容。

    这是 Docling 的特色功能，可以保留文档的表格、列表等结构化格式。

    Args:
        file_path: PDF 文件绝对路径

    Returns:
        Markdown 格式的解析内容
    """
    return parse_pdf_from_file_docling.invoke({"file_path": file_path})
