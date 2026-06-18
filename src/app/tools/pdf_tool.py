"""
PDF 解析工具。

提供同步和异步的 PDF 文件、URL、内容解析功能。
"""

import asyncio
import hashlib
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
import pymupdf4llm
from langchain_core.tools import tool

from app.core.config import settings


# --- PDF 缓存 ---

class _PDFCache:
    """基于 SHA-256 的 PDF 解析结果缓存。"""

    def __init__(self, max_size: int = 128):
        self._cache: dict[str, str] = {}
        self._max_size = max_size

    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get(self, data: bytes) -> str | None:
        key = self._hash(data)
        return self._cache.get(key)

    def set(self, data: bytes, result: str) -> None:
        key = self._hash(data)
        if len(self._cache) >= self._max_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = result


@lru_cache(maxsize=1)
def _get_pdf_cache() -> _PDFCache:
    return _PDFCache(max_size=settings.pdf_max_cache_size)


# --- PyMuPDF4LLM 解析器 ---

def _parse_pdf_pymupdf(pdf_path: str) -> str:
    """使用 PyMuPDF4LLM 解析 PDF 文件。"""
    return pymupdf4llm.to_markdown(
        pdf_path,
        page_chunks=False,
        write_images=settings.pdf_extract_images,
        show_progress=False,
        table_strategy=settings.pdf_table_strategy,
    )


def _parse_pdf_bytes(pdf_bytes: bytes, filename: str | None = None) -> str:
    """解析 PDF 字节数据。"""
    cache = _get_pdf_cache()
    cached = cache.get(pdf_bytes)
    if cached is not None:
        return cached

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        result = _parse_pdf_pymupdf(tmp_path)
        cache.set(pdf_bytes, result)
        return result
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _load_pdf_from_url(url: str) -> str:
    """从 URL 下载并解析 PDF。"""
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return _parse_pdf_bytes(resp.content)


def _load_pdf_from_path(path: str) -> str:
    """从本地路径解析 PDF。"""
    pdf_path = Path(path)
    if not pdf_path.exists():
        return f"错误: 文件不存在 - {path}"
    if not pdf_path.suffix.lower() == ".pdf":
        return f"错误: 文件不是 PDF 格式 - {path}"
    return _parse_pdf_pymupdf(str(pdf_path))


# --- 同步工具 ---

@tool
def parse_pdf_from_file(path: str) -> str:
    """
    解析本地 PDF 文件并提取文本内容。

    Args:
        path: PDF 文件的本地路径

    Returns:
        提取的文本内容（Markdown 格式）或错误消息。
    """
    return _load_pdf_from_path(path)


@tool
def parse_pdf_from_content(content: str) -> str:
    """
    解析 Base64 编码的 PDF 内容。

    Args:
        content: Base64 编码的 PDF 数据

    Returns:
        提取的文本内容（Markdown 格式）或错误消息。
    """
    import base64

    try:
        pdf_bytes = base64.b64decode(content)
        return _parse_pdf_bytes(pdf_bytes)
    except Exception as e:
        return f"PDF 解析失败: {e}"


@tool
def parse_pdf_from_url(url: str) -> str:
    """
    从 URL 下载并解析 PDF 文件。

    Args:
        url: PDF 文件的 URL 地址

    Returns:
        提取的文本内容（Markdown 格式）或错误消息。
    """
    try:
        return _load_pdf_from_url(url)
    except Exception as e:
        return f"PDF 解析失败: {e}"


# --- 异步包装 ---

async def parse_pdf_from_file_async(path: str) -> str:
    """parse_pdf_from_file 的异步版本。"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _load_pdf_from_path, path)


async def parse_pdf_from_url_async(url: str) -> str:
    """parse_pdf_from_url 的异步版本。"""
    return await asyncio.to_thread(_load_pdf_from_url, url)


async def parse_pdf_from_content_async(content: str) -> str:
    """parse_pdf_from_content 的异步版本。"""
    import base64

    def _decode_and_parse():
        pdf_bytes = base64.b64decode(content)
        return _parse_pdf_bytes(pdf_bytes)

    return await asyncio.to_thread(_decode_and_parse)
