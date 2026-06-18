"""
核心模块。

提供配置管理和状态定义。
"""

from app.core.config import settings, get_settings
from app.core.state import CustomState, ContextState

__all__ = ["settings", "get_settings", "CustomState", "ContextState"]
