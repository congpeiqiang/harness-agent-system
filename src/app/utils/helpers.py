"""
通用工具函数。

提供项目中常用的辅助函数。
"""

import os
from pathlib import Path


def get_project_root() -> Path:
    """
    获取项目根目录。

    Returns:
        项目根目录的 Path 对象
    """
    current_file = Path(__file__).resolve()
    # src/app/utils/helpers.py -> 项目根目录
    return current_file.parent.parent.parent.parent


def format_error_message(error: Exception, context: str = "") -> str:
    """
    格式化错误消息。

    Args:
        error: 异常对象
        context: 错误上下文描述

    Returns:
        格式化后的错误消息字符串
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        return f"[{context}] {error_type}: {error_msg}"
    return f"{error_type}: {error_msg}"


def ensure_directory(path: str | Path) -> Path:
    """
    确保目录存在，如不存在则创建。

    Args:
        path: 目录路径

    Returns:
        目录的 Path 对象
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
