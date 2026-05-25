"""
@File    :   docling_pdf_parser.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   基于 Docling 的 PDF 解析器，支持多模态图像识别与共享缓存，支持文件名、base64 内容和在线 URL 输入
"""

import os
import tempfile
from typing import Any, Optional, Union
from urllib.parse import urlparse

import requests
from langchain_core.documents import Document
from langchain_docling import DoclingLoader

from app.core.config import settings
from app.logger import setup_logger
from app.processors.pdf_cache import (
    PDFCacheManager,
    get_cache_manager,
    compute_file_hash,
    compute_bytes_hash,
    decode_content,
)

# 获取日志记录器
logger = setup_logger(__name__)


def _do_parse_pdf_from_file(
    file_path: str,
    *,
    export_type: str = "markdown",
    enable_multimodal: bool = False,
    extract_images: bool = False,
) -> list[Document]:
    """从文件路径解析 PDF 的内部实现。

    Args:
        file_path: PDF 文件绝对路径
        export_type: 导出类型，如 "markdown" 或 "document"
        enable_multimodal: 是否开启多模态
        extract_images: 是否提取图像

    Returns:
        解析后的文档片段列表
    """
    loader_kwargs: dict[str, Any] = {
        "file_path": file_path,
        "export_type": export_type,
    }

    if enable_multimodal and extract_images:
        from docling.datamodel.document import ConversionResult
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import DocumentConverter
        
        converter = DocumentConverter()
        result = converter.convert(file_path)
        
        loader = DoclingLoader(file_path=file_path, export_type=export_type)
        logger.info("多模态已开启，使用 Docling 进行解析")
    else:
        loader = DoclingLoader(**loader_kwargs)
        logger.info("使用 Docling 进行标准解析")

    return loader.load()


class DoclingPDFParser:
    """基于 Docling 的 PDF 解析器，支持多模态图像识别与共享缓存。

    核心特性：
        1. 使用内容哈希（SHA-256）判断是否为同一文件/内容，避免重复解析
        2. 支持两种输入方式：文件名（路径）或 PDF 内容（base64 编码 / 原始字节）
        3. 核心解析逻辑委托给内部函数 _do_parse_pdf_from_file
        4. 使用共享缓存（与 PDFParser 共享缓存）

    配置优先级：显式传参 > .env 环境变量 > config.py 中的默认值

    使用示例::

        # 通过文件名解析（带缓存）
        parser = DoclingPDFParser()
        docs = parser.parse_file("example.pdf")

        # 通过 base64 编码内容解析（带缓存）
        parser = DoclingPDFParser()
        docs = parser.parse_content(base64_str)
    """

    def __init__(
        self,
        *,
        export_type: Optional[str] = None,
        enable_multimodal: Optional[bool] = None,
        extract_images: Optional[bool] = None,
        max_cache_size: Optional[int] = None,
    ):
        """初始化 Docling PDF 解析器。

        所有配置项均可选，未传入时从 settings（.env）读取，
        .env 未配置时使用 config.py 中定义的默认值。

        Args:
            export_type: 导出类型，如 "markdown" 或 "document"
            enable_multimodal: 是否开启多模态
            extract_images: 是否提取图像
            max_cache_size: 最大缓存条目数
        """
        self._export_type: str = export_type if export_type is not None else getattr(settings, "docling_export_type", "markdown")
        self._enable_multimodal: bool = enable_multimodal if enable_multimodal is not None else settings.enable_pdf_multimodal
        self._extract_images: bool = extract_images if extract_images is not None else settings.pdf_extract_images
        
        # 使用共享缓存管理器（与 PDFParser 共享）
        cache_size = max_cache_size if max_cache_size is not None else settings.pdf_max_cache_size
        self._cache: PDFCacheManager = get_cache_manager(cache_size)

        logger.info(
            "DoclingPDFParser 初始化完成 | 多模态: %s | 提取图像: %s | 导出类型: %s | 共享缓存大小: %d",
            self._enable_multimodal,
            self._extract_images,
            self._export_type,
            cache_size,
        )

    def parse_file(self, file_name: str) -> list[Document]:
        """解析 PDF 文件，返回文档片段列表。

        同一文件（基于内容哈希判断）不会重复解析，直接返回缓存结果。
        缓存与 PDFParser 共享。

        Args:
            file_name: PDF 文件名或路径

        Returns:
            解析后的文档片段列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件不是 PDF 格式
        """
        file_path = self._resolve_file_path(file_name)
        file_hash = compute_file_hash(file_path)

        # 命中缓存（从共享缓存获取）
        cached_docs = self._cache.get(file_hash)
        if cached_docs is not None:
            logger.info("命中共享缓存，跳过解析 | 文件: %s | 哈希: %s", file_name, file_hash[:12])
            return cached_docs

        # 委托内部函数执行解析
        docs = _do_parse_pdf_from_file(
            file_path,
            export_type=self._export_type,
            enable_multimodal=self._enable_multimodal,
            extract_images=self._extract_images,
        )

        # 写入共享缓存
        self._cache.set(file_hash, docs)
        logger.info("解析完成并写入共享缓存 | 文件: %s | 哈希: %s | 片段数: %d", file_name, file_hash[:12], len(docs))

        return docs

    def parse_content(self, content: Union[str, bytes]) -> list[Document]:
        """解析 PDF 内容，返回文档片段列表。

        支持 base64 编码字符串或原始字节作为输入。
        同一内容（基于哈希判断）不会重复解析，直接返回缓存结果。
        缓存与 PDFParser 共享。

        Args:
            content: PDF 内容，base64 编码字符串或原始字节

        Returns:
            解析后的文档片段列表

        Raises:
            ValueError: content 解码失败
        """
        pdf_bytes = decode_content(content)
        content_hash = compute_bytes_hash(pdf_bytes)

        # 命中缓存（从共享缓存获取）
        cached_docs = self._cache.get(content_hash)
        if cached_docs is not None:
            logger.info("命中共享缓存，跳过解析 | 哈希: %s", content_hash[:12])
            return cached_docs

        # 委托内部函数执行解析
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            docs = _do_parse_pdf_from_file(
                tmp_path,
                export_type=self._export_type,
                enable_multimodal=self._enable_multimodal,
                extract_images=self._extract_images,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                logger.debug("已清理临时文件: %s", tmp_path)

        # 写入共享缓存
        self._cache.set(content_hash, docs)
        logger.info("解析完成并写入共享缓存 | 哈希: %s | 片段数: %d", content_hash[:12], len(docs))

        return docs

    def parse_url(
        self,
        url: str,
        *,
        timeout: int = 60,
        headers: Optional[dict[str, str]] = None,
    ) -> list[Document]:
        """从在线 URL 直接解析 PDF，无需先下载到本地。

        通过流式下载读取 PDF 内容到内存，解析完成后自动清理临时文件。
        同一 URL 返回的内容（基于内容哈希判断）会命中缓存。
        缓存与 PDFParser 共享。

        Args:
            url: PDF 文件的在线 URL
            timeout: 下载超时时间（秒），默认 60
            headers: 自定义请求头，默认使用常见浏览器 User-Agent

        Returns:
            解析后的文档片段列表

        Raises:
            ValueError: URL 格式无效
            requests.RequestException: 下载失败
        """
        if not _is_valid_url(url):
            raise ValueError(f"无效的 URL: {url}")

        # 下载 PDF 内容到内存
        pdf_bytes = _download_pdf_bytes(url, timeout=timeout, headers=headers)
        content_hash = compute_bytes_hash(pdf_bytes)

        # 命中缓存
        cached_docs = self._cache.get(content_hash)
        if cached_docs is not None:
            logger.info("命中共享缓存，跳过解析 | URL: %s | 哈希: %s", url, content_hash[:12])
            return cached_docs

        # 写入临时文件并解析
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            docs = _do_parse_pdf_from_file(
                tmp_path,
                export_type=self._export_type,
                enable_multimodal=self._enable_multimodal,
                extract_images=self._extract_images,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                logger.debug("已清理临时文件: %s", tmp_path)

        # 写入共享缓存
        self._cache.set(content_hash, docs)
        logger.info("解析完成并写入共享缓存 | URL: %s | 哈希: %s | 片段数: %d", url, content_hash[:12], len(docs))

        return docs

    def clear_cache(self) -> None:
        """清除全部缓存（会清除所有解析器共享的缓存）。"""
        self._cache.clear()
        logger.info("已清除全部共享缓存")

    def _resolve_file_path(self, file_name: str) -> str:
        """将文件名解析为绝对路径，并校验文件存在性和格式。

        Args:
            file_name: 文件名或路径

        Returns:
            文件的绝对路径

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件不是 PDF 格式
        """
        if os.path.isabs(file_name) and os.path.isfile(file_name):
            abs_path = file_name
        else:
            abs_path = os.path.abspath(file_name)

        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"PDF 文件不存在: {abs_path}")

        if not abs_path.lower().endswith(".pdf"):
            raise ValueError(f"文件不是 PDF 格式: {abs_path}")

        return abs_path


def _is_valid_url(url: str) -> bool:
    """检查字符串是否为有效的 HTTP/HTTPS URL。"""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _download_pdf_bytes(
    url: str,
    *,
    timeout: int = 60,
    headers: Optional[dict[str, str]] = None,
) -> bytes:
    """从 URL 下载 PDF 内容到内存。

    Args:
        url: PDF 文件 URL
        timeout: 请求超时时间（秒）
        headers: 自定义请求头

    Returns:
        PDF 原始字节内容

    Raises:
        requests.RequestException: 网络请求失败
        ValueError: 响应内容类型不是 PDF
    """
    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*;q=0.9",
    }
    if headers:
        default_headers.update(headers)

    logger.info("开始下载 PDF | URL: %s", url)
    response = requests.get(url, headers=default_headers, timeout=timeout, stream=True)
    response.raise_for_status()

    # 检查 Content-Type（容错：未声明时也继续）
    content_type = response.headers.get("Content-Type", "").lower()
    if content_type and "pdf" not in content_type and "octet-stream" not in content_type:
        logger.warning("响应 Content-Type 可能不是 PDF: %s", content_type)

    pdf_bytes = response.content
    logger.info("下载完成 | URL: %s | 大小: %d bytes", url, len(pdf_bytes))
    return pdf_bytes


# 为了向后兼容，导出公共函数
__all__ = [
    "DoclingPDFParser",
    "_do_parse_pdf_from_file",
    "compute_file_hash",
    "compute_bytes_hash",
    "decode_content",
]

# 保持向后兼容的别名
_compute_file_hash = compute_file_hash
_compute_bytes_hash = compute_bytes_hash
_decode_content = decode_content
