"""
@File    :   pdf_cache.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   PDF 解析器共享缓存模块

提供统一的缓存管理，供所有 PDF 解析器共享使用。
"""

import base64
import hashlib
import threading
from typing import Optional, Union

from langchain_core.documents import Document


class PDFCacheManager:
    """PDF 解析结果共享缓存管理器。
    
    使用单例模式确保所有解析器共享同一个缓存实例。
    支持线程安全的缓存操作。
    
    缓存策略:
        - 使用 SHA-256 哈希作为缓存键
        - FIFO (先进先出) 淘汰策略
        - 线程安全读写
    """
    
    _instance: Optional["PDFCacheManager"] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls, max_cache_size: int = 128) -> "PDFCacheManager":
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_cache_size: int = 128):
        """初始化缓存管理器。
        
        Args:
            max_cache_size: 最大缓存条目数，默认 128
        """
        # 避免重复初始化
        if getattr(self, '_initialized', False):
            return
        
        self._max_cache_size: int = max_cache_size
        self._cache: dict[str, list[Document]] = {}
        self._cache_lock: threading.RLock = threading.RLock()
        self._initialized = True
    
    def get(self, key: str) -> Optional[list[Document]]:
        """获取缓存值。
        
        Args:
            key: 缓存键（哈希值）
            
        Returns:
            缓存的文档列表，不存在则返回 None
        """
        with self._cache_lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: list[Document]) -> None:
        """设置缓存值。
        
        如果缓存已满，自动淘汰最早的条目。
        
        Args:
            key: 缓存键（哈希值）
            value: 要缓存的文档列表
        """
        with self._cache_lock:
            # 缓存容量控制
            if len(self._cache) >= self._max_cache_size and key not in self._cache:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            self._cache[key] = value
    
    def clear(self) -> None:
        """清除全部缓存"""
        with self._cache_lock:
            self._cache.clear()
    
    def contains(self, key: str) -> bool:
        """检查缓存是否包含指定键
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        with self._cache_lock:
            return key in self._cache
    
    def size(self) -> int:
        """获取当前缓存条目数"""
        with self._cache_lock:
            return len(self._cache)
    
    def keys(self) -> list[str]:
        """获取所有缓存键（用于调试）"""
        with self._cache_lock:
            return list(self._cache.keys())


def get_cache_manager(max_cache_size: int = 128) -> PDFCacheManager:
    """获取共享缓存管理器实例。
    
    这是获取缓存管理器的推荐方式。
    
    Args:
        max_cache_size: 最大缓存条目数
        
    Returns:
        PDFCacheManager 实例
    """
    return PDFCacheManager(max_cache_size)


def compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """计算文件的 SHA-256 哈希值。
    
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


def compute_bytes_hash(data: bytes) -> str:
    """计算字节内容的 SHA-256 哈希值。
    
    Args:
        data: 字节内容
        
    Returns:
        内容的 SHA-256 十六进制摘要
    """
    return hashlib.sha256(data).hexdigest()


def decode_content(content: Union[str, bytes]) -> bytes:
    """将输入内容解码为原始字节。
    
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


# 别名：SharedCache 与 PDFCacheManager 相同，用于向后兼容
SharedCache = PDFCacheManager
