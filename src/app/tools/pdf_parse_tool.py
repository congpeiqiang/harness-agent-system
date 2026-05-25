"""
@File    :   pdf_parse_tool.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   PyMuPDF 的 PDF 解析 Tool，供 LangChain 调用，使用共享缓存
"""

from typing import Union

from langchain_core.tools import tool
from langchain_core.documents import Document

from app.core.config import settings
from app.logger import setup_logger
from app.processors.pdf_parser import PDFParser
from app.processors.pdf_cache import get_cache_manager, PDFCacheManager

# 获取日志记录器
logger = setup_logger(__name__)

# 创建模块级共享缓存管理器
_cache_manager = get_cache_manager()

# 创建模块级单例解析器（内部自动使用共享缓存）
_pdf_parser = PDFParser()


@tool
def parse_pdf_from_file(
    file_name: str,
    *,
    enable_multimodal: bool = False,
) -> str:
    """使用 PyMuPDF 解析本地 PDF 文件，返回文本内容。

    Args:
        file_name: PDF 文件名或路径
        enable_multimodal: 是否开启多模态（提取图像并识别）

    Returns:
        PDF 文本内容，失败时返回错误信息
    """
    try:
        logger.info("开始解析 PDF | 文件: %s | 多模态: %s", file_name, enable_multimodal)
        
        # 使用共享的解析器实例
        docs: list[Document] = _pdf_parser.parse_file(file_name)
        
        if not docs:
            logger.warning("PDF 解析结果为空 | 文件: %s", file_name)
            return "解析结果为空，PDF 可能无内容"

        # 拼接文档内容
        text_parts = []
        for doc in docs:
            text_parts.append(doc.page_content)
            # 添加元数据信息（可选）
            if doc.metadata:
                text_parts.append(f"\n[元数据: {doc.metadata}]")

        full_text = "\n\n---\n\n".join(text_parts)
        logger.info("PDF 解析完成 | 文件: %s | 片段数: %d | 文本长度: %d", file_name, len(docs), len(full_text))
        return full_text

    except FileNotFoundError as e:
        logger.error("文件不存在: %s | %s", file_name, e)
        return f"错误: 文件不存在 - {file_name}"
    except ValueError as e:
        logger.error("文件格式错误: %s | %s", file_name, e)
        return f"错误: 文件格式错误 - {e}"
    except Exception as e:
        logger.exception("PDF 解析失败 | 文件: %s | 错误: %s", file_name, e)
        return f"错误: PDF 解析失败 - {str(e)}"


@tool
def parse_pdf_from_content(
    content: str,
    *,
    enable_multimodal: bool = False,
) -> str:
    """使用 PyMuPDF 解析 base64 编码的 PDF 内容，返回文本内容。

    Args:
        content: base64 编码的 PDF 内容
        enable_multimodal: 是否开启多模态（提取图像并识别）

    Returns:
        PDF 文本内容，失败时返回错误信息
    """
    try:
        logger.info("开始解析 PDF 内容 | 多模态: %s", enable_multimodal)
        
        # 使用共享的解析器实例
        docs: list[Document] = _pdf_parser.parse_content(content)
        
        if not docs:
            logger.warning("PDF 内容解析结果为空")
            return "解析结果为空，PDF 可能无内容"

        # 拼接文档内容
        text_parts = []
        for doc in docs:
            text_parts.append(doc.page_content)
            if doc.metadata:
                text_parts.append(f"\n[元数据: {doc.metadata}]")

        full_text = "\n\n---\n\n".join(text_parts)
        logger.info("PDF 内容解析完成 | 片段数: %d | 文本长度: %d", len(docs), len(full_text))
        return full_text

    except ValueError as e:
        logger.error("PDF 内容格式错误: %s", e)
        return f"错误: PDF 内容格式错误 - {e}"
    except Exception as e:
        logger.exception("PDF 内容解析失败: %s", e)
        return f"错误: PDF 内容解析失败 - {str(e)}"


@tool
def clear_pdf_cache() -> str:
    """清除 PyMuPDF PDF 解析器的共享缓存。

    注意: 这会清除所有解析器共享的缓存，包括 Docling 解析器的缓存。

    Returns:
        操作结果信息
    """
    try:
        cache_manager = get_cache_manager()
        stats_before = cache_manager.get_stats()
        cache_manager.clear_all()
        stats_after = cache_manager.get_stats()
        logger.info("已清除共享缓存 | 清除前: %s | 清除后: %s", stats_before, stats_after)
        return f"共享缓存已清除 | 清除前: {stats_before}"
    except Exception as e:
        logger.exception("清除缓存失败: %s", e)
        return f"错误: 清除缓存失败 - {str(e)}"


@tool
def get_cache_stats() -> str:
    """获取 PyMuPDF PDF 解析器的共享缓存状态。

    Returns:
        缓存状态信息
    """
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()
        return f"共享缓存状态: {stats}"
    except Exception as e:
        logger.exception("获取缓存状态失败: %s", e)
        return f"错误: 获取缓存状态失败 - {str(e)}"
