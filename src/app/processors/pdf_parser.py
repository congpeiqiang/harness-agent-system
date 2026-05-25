"""
@File    :   pdf_parser.py
@Author  :   CodeGeeX
@Time    :   2026/5/22
@Desc    :   PDF 解析器，支持多模态图像识别与文件哈希缓存，支持文件名、base64 内容和在线 URL 输入
"""

import os
import tempfile
from typing import Any, Optional, Union
from urllib.parse import urlparse

import requests
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

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
    mode: str = "single",
    table_strategy: str = "lines",
    enable_multimodal: bool = False,
    extract_images: bool = False,
    custom_images_parser: Optional[Any] = None,
) -> list[Document]:
    """从文件路径解析 PDF 的内部实现，供 @tool 函数和 PDFParser 类共用。

    Args:
        file_path: PDF 文件绝对路径
        mode: 解析模式
        table_strategy: 表格解析策略
        enable_multimodal: 是否开启多模态
        extract_images: 是否提取图像
        custom_images_parser: 自定义图像解析器

    Returns:
        解析后的文档片段列表
    """
    loader_kwargs: dict[str, Any] = {
        "file_path": file_path,
        "mode": mode,
        "table_strategy": table_strategy,
    }

    if enable_multimodal:
        loader_kwargs["extract_images"] = extract_images
        if custom_images_parser is not None:
            loader_kwargs["images_parser"] = custom_images_parser
        else:
            from langchain_community.document_loaders.parsers import LLMImageBlobParser
            from app.core.llms import image_llm_model
            loader_kwargs["images_parser"] = LLMImageBlobParser(model=image_llm_model)
        logger.info("多模态已开启，已添加 images_parser")

    loader = PyMuPDF4LLMLoader(**loader_kwargs)
    return loader.load()


class PDFParser:
    """PDF 解析器，支持多模态图像识别与文件哈希缓存。

    核心特性：
        1. 使用内容哈希（SHA-256）判断是否为同一文件/内容，避免重复解析
        2. 支持两种输入方式：文件名（路径）或 PDF 内容（base64 编码 / 原始字节）
        3. 核心解析逻辑委托给内部函数 _do_parse_pdf_from_file
        4. 使用共享缓存（与 DoclingPDFParser 共享缓存）

    配置优先级：显式传参 > .env 环境变量 > config.py 中的默认值

    使用示例::

        # 通过文件名解析（带缓存）
        parser = PDFParser()
        docs = parser.parse_file("example.pdf")

        # 通过 base64 编码内容解析（带缓存）
        parser = PDFParser()
        docs = parser.parse_content(base64_str)
    """

    def __init__(
        self,
        *,
        mode: Optional[str] = None,
        table_strategy: Optional[str] = None,
        enable_multimodal: Optional[bool] = None,
        extract_images: Optional[bool] = None,
        max_cache_size: Optional[int] = None,
        custom_images_parser: Optional[Any] = None,
    ):
        """初始化 PDF 解析器。

        所有配置项均可选，未传入时从 settings（.env）读取，
        .env 未配置时使用 config.py 中定义的默认值。

        Args:
            mode: 解析模式，覆盖 settings.pdf_mode
            table_strategy: 表格解析策略，覆盖 settings.pdf_table_strategy
            enable_multimodal: 是否开启多模态，覆盖 settings.enable_pdf_multimodal
            extract_images: 是否提取图像，覆盖 settings.pdf_extract_images
            max_cache_size: 最大缓存条目数，覆盖 settings.pdf_max_cache_size
            custom_images_parser: 自定义图像解析器，若为 None 且开启多模态，
                                  则使用默认的 LLMImageBlobParser
        """
        # 优先使用显式传入的参数，否则从 settings（.env / config.py 默认值）读取
        self._mode: str = mode if mode is not None else settings.pdf_mode
        self._table_strategy: str = table_strategy if table_strategy is not None else settings.pdf_table_strategy
        self._enable_multimodal: bool = enable_multimodal if enable_multimodal is not None else settings.enable_pdf_multimodal
        self._extract_images: bool = extract_images if extract_images is not None else settings.pdf_extract_images
        
        # 使用共享缓存管理器
        cache_size = max_cache_size if max_cache_size is not None else settings.pdf_max_cache_size
        self._cache: PDFCacheManager = get_cache_manager(cache_size)

        self._custom_images_parser = custom_images_parser

        logger.info(
            "PDFParser 初始化完成 | 多模态: %s | 提取图像: %s | 模式: %s | 共享缓存大小: %d",
            self._enable_multimodal,
            self._extract_images,
            self._mode,
            cache_size,
        )

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def parse_file(self, file_name: str) -> list[Document]:
        """解析 PDF 文件，返回文档片段列表。

        同一文件（基于内容哈希判断）不会重复解析，直接返回缓存结果。
        缓存与 DoclingPDFParser 共享。

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
            mode=self._mode,
            table_strategy=self._table_strategy,
            enable_multimodal=self._enable_multimodal,
            extract_images=self._extract_images,
            custom_images_parser=self._custom_images_parser,
        )

        # 写入共享缓存
        self._cache.set(file_hash, docs)
        logger.info("解析完成并写入共享缓存 | 文件: %s | 哈希: %s | 片段数: %d", file_name, file_hash[:12], len(docs))

        return docs

    def parse_content(self, content: Union[str, bytes]) -> list[Document]:
        """解析 PDF 内容，返回文档片段列表。

        支持 base64 编码字符串或原始字节作为输入。
        同一内容（基于哈希判断）不会重复解析，直接返回缓存结果。
        缓存与 DoclingPDFParser 共享。

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
                mode=self._mode,
                table_strategy=self._table_strategy,
                enable_multimodal=self._enable_multimodal,
                extract_images=self._extract_images,
                custom_images_parser=self._custom_images_parser,
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

        PyMuPDF4LLMLoader 支持直接传入 URL 进行解析，无需手动下载。
        同一 URL 返回的内容（基于内容哈希判断）会命中缓存。
        缓存与 DoclingPDFParser 共享。

        Args:
            url: PDF 文件的在线 URL
            timeout: 下载超时时间（秒），默认 60（当前版本作为兼容性保留）
            headers: 自定义请求头（当前版本作为兼容性保留）

        Returns:
            解析后的文档片段列表

        Raises:
            ValueError: URL 格式无效
            Exception: 解析失败
        """
        if not _is_valid_url(url):
            raise ValueError(f"无效的 URL: {url}")

        # 使用 URL 本身作为缓存键（因为 PyMuPDF4LLMLoader 内部会处理下载）
        # 先尝试从缓存获取
        url_hash = compute_bytes_hash(url.encode("utf-8"))
        cached_docs = self._cache.get(url_hash)
        if cached_docs is not None:
            logger.info("命中共享缓存，跳过解析 | URL: %s | 哈希: %s", url, url_hash[:12])
            return cached_docs

        # 直接传入 URL 给 PyMuPDF4LLMLoader 进行解析
        logger.info("开始从 URL 解析 PDF | URL: %s", url)
        docs = _do_parse_pdf_from_file(
            url,
            mode=self._mode,
            table_strategy=self._table_strategy,
            enable_multimodal=self._enable_multimodal,
            extract_images=self._extract_images,
            custom_images_parser=self._custom_images_parser,
        )

        # 写入共享缓存
        self._cache.set(url_hash, docs)
        logger.info("解析完成并写入共享缓存 | URL: %s | 哈希: %s | 片段数: %d", url, url_hash[:12], len(docs))

        return docs

    def clear_cache(self) -> None:
        """清除全部缓存（会清除所有解析器共享的缓存）。"""
        self._cache.clear()
        logger.info("已清除全部共享缓存")

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

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
        # 如果已经是绝对路径且存在，直接使用
        if os.path.isabs(file_name) and os.path.isfile(file_name):
            abs_path = file_name
        else:
            # 尝试基于当前工作目录解析
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
    "PDFParser",
    "_do_parse_pdf_from_file",
    "compute_file_hash",
    "compute_bytes_hash",
    "decode_content",
]

# 保持向后兼容的别名
_compute_file_hash = compute_file_hash
_compute_bytes_hash = compute_bytes_hash
_decode_content = decode_content
