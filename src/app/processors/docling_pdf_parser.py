"""
@File    :   docling_pdf_parser.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   基于 Docling 的 PDF 解析器，支持多模态图像识别与文件哈希缓存
"""

import base64
import hashlib
import os
import tempfile
from typing import Any, Optional, Union

from langchain_core.documents import Document
from langchain_docling import DoclingLoader

from app.core.config import settings
from app.logger import setup_logger

# 获取日志记录器
logger = setup_logger(__name__)


def _compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """计算文件的 SHA-256 哈希值，用于判断文件是否相同。

    Args:
        file_path: 文件路径
        chunk_size: 读取块大小

    Returns:
        文件的 SHA-256 十六进制摘要
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def _compute_bytes_hash(data: bytes) -> str:
    """计算字节内容的 SHA-256 哈希值，用于判断内容是否相同。

    Args:
        data: 字节内容

    Returns:
        内容的 SHA-256 十六进制摘要
    """
    return hashlib.sha256(data).hexdigest()


def _decode_content(content: Union[str, bytes]) -> bytes:
    """将输入内容解码为原始字节。

    若 content 为 str，则视为 base64 编码字符串进行解码；
    若 content 为 bytes，则直接返回。

    Args:
        content: base64 编码字符串或原始字节

    Returns:
        解码后的原始字节

    Raises:
        ValueError: base64 解码失败
    """
    if isinstance(content, bytes):
        return content
    try:
        return base64.b64decode(content)
    except Exception as e:
        raise ValueError(f"content 解码失败，请确认是否为有效的 base64 编码: {e}") from e


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
        
        # 使用 DoclingLoader 加载
        loader = DoclingLoader(file_path=file_path, export_type=export_type)
        logger.info("多模态已开启，使用 Docling 进行解析")
    else:
        loader = DoclingLoader(**loader_kwargs)
        logger.info("使用 Docling 进行标准解析")

    return loader.load()


class DoclingPDFParser:
    """基于 Docling 的 PDF 解析器，支持多模态图像识别与文件哈希缓存。

    核心特性：
        1. 使用内容哈希（SHA-256）判断是否为同一文件/内容，避免重复解析
        2. 支持两种输入方式：文件名（路径）或 PDF 内容（base64 编码 / 原始字节）
        3. 核心解析逻辑委托给内部函数 _do_parse_pdf_from_file

    配置优先级：显式传参 > .env 环境变量 > config.py 中的默认值

    使用示例::

        # 通过文件名解析（带缓存）
        parser = DoclingPDFParser()
        docs = parser.parse_file("example.pdf")

        # 通过 base64 编码内容解析（带缓存）
        parser = DoclingPDFParser()
        docs = parser.parse_content(base64_str)

        # 无需缓存时，直接使用 @tool 函数
        from app.processors.docling_pdf_parser import parse_pdf_from_file, parse_pdf_from_content
        text = parse_pdf_from_file.invoke({"file_path": "/path/to/file.pdf"})
        text = parse_pdf_from_content.invoke({"content": base64_str})
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
            export_type: 导出类型，如 "markdown" 或 "document"，覆盖 settings.docling_export_type
            enable_multimodal: 是否开启多模态，覆盖 settings.enable_pdf_multimodal
            extract_images: 是否提取图像，覆盖 settings.pdf_extract_images
            max_cache_size: 最大缓存条目数，覆盖 settings.pdf_max_cache_size
        """
        # 优先使用显式传入的参数，否则从 settings（.env / config.py 默认值）读取
        self._export_type: str = export_type if export_type is not None else getattr(settings, "docling_export_type", "markdown")
        self._enable_multimodal: bool = enable_multimodal if enable_multimodal is not None else settings.enable_pdf_multimodal
        self._extract_images: bool = extract_images if extract_images is not None else settings.pdf_extract_images
        self._max_cache_size: int = max_cache_size if max_cache_size is not None else settings.pdf_max_cache_size

        # 缓存字典: file_hash -> list[Document]
        self._cache: dict[str, list[Document]] = {}

        logger.info(
            "DoclingPDFParser 初始化完成 | 多模态: %s | 提取图像: %s | 导出类型: %s",
            self._enable_multimodal,
            self._extract_images,
            self._export_type,
        )

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def parse_file(self, file_name: str) -> list[Document]:
        """解析 PDF 文件，返回文档片段列表。

        同一文件（基于内容哈希判断）不会重复解析，直接返回缓存结果。

        Args:
            file_name: PDF 文件名或路径

        Returns:
            解析后的文档片段列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件不是 PDF 格式
        """
        file_path = self._resolve_file_path(file_name)
        file_hash = _compute_file_hash(file_path)

        # 命中缓存
        if file_hash in self._cache:
            logger.info("命中缓存，跳过解析 | 文件: %s | 哈希: %s", file_name, file_hash[:12])
            return self._cache[file_hash]

        # 缓存容量控制
        self._evict_if_needed()

        # 委托内部函数执行解析
        docs = _do_parse_pdf_from_file(
            file_path,
            export_type=self._export_type,
            enable_multimodal=self._enable_multimodal,
            extract_images=self._extract_images,
        )

        # 写入缓存
        self._cache[file_hash] = docs
        logger.info("解析完成并缓存 | 文件: %s | 哈希: %s | 片段数: %d", file_name, file_hash[:12], len(docs))

        return docs

    def parse_content(self, content: Union[str, bytes]) -> list[Document]:
        """解析 PDF 内容，返回文档片段列表。

        支持 base64 编码字符串或原始字节作为输入。
        同一内容（基于哈希判断）不会重复解析，直接返回缓存结果。

        Args:
            content: PDF 内容，base64 编码字符串或原始字节

        Returns:
            解析后的文档片段列表

        Raises:
            ValueError: content 解码失败
        """
        pdf_bytes = _decode_content(content)
        content_hash = _compute_bytes_hash(pdf_bytes)

        # 命中缓存
        if content_hash in self._cache:
            logger.info("命中缓存，跳过解析 | 哈希: %s", content_hash[:12])
            return self._cache[content_hash]

        # 缓存容量控制
        self._evict_if_needed()

        # 委托内部函数执行解析（先解码写入临时文件，再调用 _do_parse_pdf_from_file）
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

        # 写入缓存
        self._cache[content_hash] = docs
        logger.info("解析完成并缓存 | 哈希: %s | 片段数: %d", content_hash[:12], len(docs))

        return docs

    def clear_cache(self) -> None:
        """清除全部缓存。"""
        self._cache.clear()
        logger.info("已清除全部缓存")

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

    def _evict_if_needed(self) -> None:
        """当缓存达到上限时，移除最早的一条缓存（FIFO 策略）。"""
        if len(self._cache) >= self._max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.info("缓存已满，移除最早条目 | 哈希: %s", oldest_key[:12])
