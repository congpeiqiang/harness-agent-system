"""
@File    :  agent.py
@Author  :  CongPeiQiang
@Time    :  2026/5/18 19:39
@Desc    :
"""
"""
环境变量配置模块

统一管理项目中的所有环境变量，提供类型安全的配置访问。
使用 Pydantic Settings 进行配置验证和加载。

使用方法:
    from src.app.core.config import settings
    
    # 访问配置
    api_key = settings.deepseek_api_key
    model = settings.deepseek_model
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    # src/app/core/config.py -> 项目根目录
    return current_file.parent.parent.parent.parent


class AISettings(BaseSettings):
    """AI 模型相关配置"""
    
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )
    
    # DeepSeek 配置
    deepseek_api_key: Optional[str] = Field(
        default=None,
        description="DeepSeek API Key"
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API 基础 URL"
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek 模型名称"
    )
    deepseek_temperature: float = Field(
        default=0.3,
        description="DeepSeek 温度参数",
        ge=0.0,
        le=2.0
    )
    deepseek_max_input_tokens: int = Field(
        default=120000,
        description="DeepSeek 最大输入 token 数"
    )
    
    # 视觉模型 (Vision) / 豆包配置
    vision_api_key: Optional[str] = Field(
        default=None,
        description="火山引擎 API Key"
    )
    vision_base_url: str = Field(
        default="https://ark.cn-beijing.volces.com/api/v3",
        description="火山引擎 API 基础 URL"
    )
    vision_model: str = Field(
        default="doubao-seed-1-6-vision-250815",
        description="火山引擎视觉模型名称"
    )
    vision_text_model: str = Field(
        default="doubao-seed-2-0-lite-260215",
        description="火山引擎文本模型名称"
    )
    
    # OpenAI 配置 (兼容格式)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API Key"
    )
    openai_base_url: Optional[str] = Field(
        default=None,
        description="OpenAI API 基础 URL"
    )
    openai_model: Optional[str] = Field(
        default=None,
        description="OpenAI 模型名称"
    )
    enable_pdf_multimodal: bool = Field(
        default=False,
        description="是否开启pdf中的多模态解析"
    )
    pdf_mode: str = Field(
        default="single",
        description="PDF 解析模式，如 single 或 page"
    )
    pdf_table_strategy: str = Field(
        default="lines",
        description="PDF 表格解析策略，如 lines、text 等"
    )
    pdf_extract_images: bool = Field(
        default=False,
        description="是否提取 PDF 图像（仅 enable_pdf_multimodal=True 时生效）"
    )
    pdf_max_cache_size: int = Field(
        default=128,
        description="PDF 解析器最大缓存条目数",
        ge=1
    )

class LoggingSettings(BaseSettings):
    """日志相关配置"""
    
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )
    
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别是否有效"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"无效的日志级别: {v}, 必须是以下之一: {valid_levels}")
        return upper_v


class Settings(BaseSettings):
    """
    全局配置类
    
    聚合所有配置子类，提供统一的环境变量访问接口。
    自动从项目根目录的 .env 文件加载配置。
    """
    
    model_config = SettingsConfigDict(
        # 从 .env 文件加载
        env_file=get_project_root() / ".env",
        env_file_encoding="utf-8",
        # 允许大小写不敏感
        case_sensitive=False,
        # 忽略额外字段
        extra="ignore",
        # 允许通过环境变量前缀设置
        env_prefix="",
    )
    
    # 包含子配置
    ai: AISettings = Field(default_factory=AISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    # 便捷属性 - AI 配置
    @property
    def deepseek_api_key(self) -> Optional[str]:
        """获取 DeepSeek API Key"""
        # 优先从环境变量获取，然后才是 .env 文件
        return os.getenv("DEEPSEEK_API_KEY") or self.ai.deepseek_api_key
    
    @property
    def deepseek_model(self) -> str:
        """获取 DeepSeek 模型名称"""
        return self.ai.deepseek_model
    
    @property
    def deepseek_base_url(self) -> str:
        """获取 DeepSeek 基础 URL"""
        return self.ai.deepseek_base_url
    
    @property
    def vision_api_key(self) -> Optional[str]:
        """获取火山引擎 API Key"""
        return os.getenv("VISION_API_KEY") or self.ai.vision_api_key
    
    @property
    def vision_model(self) -> str:
        """获取火山引擎视觉模型名称"""
        return self.ai.vision_model
    
    @property
    def vision_text_model(self) -> str:
        """获取火山引擎文本模型名称"""
        return self.ai.vision_text_model
    
    @property
    def vision_base_url(self) -> str:
        """获取火山引擎基础 URL"""
        return self.ai.vision_base_url
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """获取 OpenAI API Key"""
        return os.getenv("OPENAI_API_KEY") or self.ai.openai_api_key

    # PDF 解析器配置便捷属性
    @property
    def enable_pdf_multimodal(self) -> bool:
        """获取是否开启 PDF 多模态解析"""
        return self.ai.enable_pdf_multimodal

    @property
    def pdf_mode(self) -> str:
        """获取 PDF 解析模式"""
        return self.ai.pdf_mode

    @property
    def pdf_table_strategy(self) -> str:
        """获取 PDF 表格解析策略"""
        return self.ai.pdf_table_strategy

    @property
    def pdf_extract_images(self) -> bool:
        """获取是否提取 PDF 图像"""
        return self.ai.pdf_extract_images

    @property
    def pdf_max_cache_size(self) -> int:
        """获取 PDF 最大缓存条目数"""
        return self.ai.pdf_max_cache_size

    # 便捷属性 - 日志配置
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self.logging.log_level
    
    def to_environment_dict(self) -> dict:
        """
        将配置转换为环境变量字典，用于启动服务器等场景
        
        Returns:
            环境变量键值对字典
        """
        return {
            # AI 配置
            "DEEPSEEK_API_KEY": self.deepseek_api_key or "",
            "DEEPSEEK_BASE_URL": self.deepseek_base_url,
            "DEEPSEEK_MODEL": self.deepseek_model,
            "VISION_API_KEY": self.vision_api_key or "",
            "VISION_BASE_URL": self.vision_base_url,
            "VISION_MODEL": self.vision_model,
            "VISION_TEXT_MODEL": self.vision_text_model,
            "OPENAI_API_KEY": self.openai_api_key or "",
            # PDF 解析器配置
            "ENABLE_PDF_MULTIMODAL": str(self.enable_pdf_multimodal),
            "PDF_MODE": self.pdf_mode,
            "PDF_TABLE_STRATEGY": self.pdf_table_strategy,
            "PDF_EXTRACT_IMAGES": str(self.pdf_extract_images),
            "PDF_MAX_CACHE_SIZE": str(self.pdf_max_cache_size),
            # 日志配置
            "LOG_LEVEL": self.log_level,
        }
    
    def apply_to_environment(self):
        """
        将配置应用到当前进程的环境变量
        """
        for key, value in self.to_environment_dict().items():
            if value:  # 只设置非空值
                os.environ[key] = value


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例模式）
    
    使用 lru_cache 确保配置只被加载一次
    
    Returns:
        Settings 配置实例
    """
    return Settings()


# 全局配置实例
settings = get_settings()


if __name__ == "__main__":
    # 测试配置加载
    print("=" * 60)
    print("环境变量配置测试")
    print("=" * 60)
    
    print("\n【AI 配置】")
    print(f"  DeepSeek API Key: {'已设置' if settings.deepseek_api_key else '未设置'}")
    print(f"  DeepSeek Model: {settings.deepseek_model}")
    print(f"  DeepSeek Base URL: {settings.deepseek_base_url}")
    print(f"  Vision API Key: {'已设置' if settings.vision_api_key else '未设置'}")
    print(f"  Vision Model: {settings.vision_model}")
    
    print("\n【日志配置】")
    print(f"  Log Level: {settings.log_level}")
    
    print("\n" + "=" * 60)
    print("环境变量字典:")
    print("=" * 60)
    for key, value in settings.to_environment_dict().items():
        # 隐藏敏感信息
        if "key" in key.lower() or "password" in key.lower() or "secret" in key.lower():
            display_value = "***" if value else ""
        else:
            display_value = value
        print(f"  {key}={display_value}")
