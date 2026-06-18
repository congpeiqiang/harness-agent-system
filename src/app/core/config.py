"""
环境变量配置模块。

统一管理项目中的所有环境变量，提供类型安全的配置访问。
使用 Pydantic Settings 进行配置验证和加载。

使用方法:
    from app.core.config import settings

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
    """获取项目根目录。"""
    current_file = Path(__file__).resolve()
    # src/app/core/config.py -> 项目根目录
    return current_file.parent.parent.parent.parent


class AISettings(BaseSettings):
    """AI 模型相关配置。"""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # DeepSeek 配置
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API Key")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com", description="DeepSeek API 基础 URL"
    )
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek 模型名称")
    deepseek_model_provider: str = Field(default="deepseek", description="DeepSeek 模型提供商")
    deepseek_temperature: float = Field(
        default=0.3, description="DeepSeek 温度参数", ge=0.0, le=2.0
    )
    deepseek_max_input_tokens: int = Field(
        default=120000, description="DeepSeek 最大输入 token 数"
    )

    # 视觉模型 / 豆包 / 火山引擎配置
    vision_api_key: Optional[str] = Field(default=None, description="火山引擎 API Key")
    vision_base_url: str = Field(
        default="https://ark.cn-beijing.volces.com/api/v3",
        description="火山引擎 API 基础 URL",
    )
    vision_model: str = Field(
        default="doubao-seed-1-6-vision-250815", description="视觉模型名称"
    )
    vision_text_model: str = Field(
        default="doubao-seed-2-0-lite-260215", description="视觉文本模型名称"
    )

    # OpenAI 兼容配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_base_url: Optional[str] = Field(default=None, description="OpenAI API 基础 URL")
    openai_model: Optional[str] = Field(default=None, description="OpenAI 模型名称")

    # PDF 解析器配置
    enable_pdf_multimodal: bool = Field(default=False, description="是否开启 PDF 多模态解析")
    pdf_mode: str = Field(default="single", description="PDF 解析模式（single 或 page）")
    pdf_table_strategy: str = Field(default="lines", description="PDF 表格解析策略")
    pdf_extract_images: bool = Field(
        default=False, description="是否提取 PDF 图像（需开启 enable_pdf_multimodal）"
    )
    pdf_max_cache_size: int = Field(default=128, description="PDF 解析器最大缓存条目数", ge=1)


class LoggingSettings(BaseSettings):
    """日志相关配置。"""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    log_level: str = Field(default="INFO", description="日志级别")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别是否有效。"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper_v = v.upper()
        if upper_v not in valid_levels:
            msg = f"无效的日志级别: {v}，必须是以下之一: {valid_levels}"
            raise ValueError(msg)
        return upper_v


class SecuritySettings(BaseSettings):
    """安全相关配置。"""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: Optional[str] = Field(default=None, description="API 认证密钥")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="允许的 CORS 来源（逗号分隔）",
    )
    rate_limit_per_minute: int = Field(
        default=60, description="每 IP 每分钟速率限制", ge=1
    )


class ServerSettings(BaseSettings):
    """服务器配置。"""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", description="服务器主机地址")
    port: int = Field(default=2026, description="服务器端口", ge=1, le=65535)
    workers: int = Field(default=1, description="工作进程数", ge=1)
    reload: bool = Field(default=False, description="是否启用自动重载")


class Settings(BaseSettings):
    """
    全局配置类。

    聚合所有配置子类，提供统一的环境变量访问接口。
    自动从项目根目录的 .env 文件加载配置。
    """

    model_config = SettingsConfigDict(
        env_file=get_project_root() / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="",
    )

    # 子配置
    ai: AISettings = Field(default_factory=AISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    # --- AI 便捷属性 ---

    @property
    def deepseek_api_key(self) -> Optional[str]:
        """获取 DeepSeek API Key。"""
        return os.getenv("DEEPSEEK_API_KEY") or self.ai.deepseek_api_key

    @property
    def deepseek_model(self) -> str:
        """获取 DeepSeek 模型名称。"""
        return self.ai.deepseek_model

    @property
    def deepseek_base_url(self) -> str:
        """获取 DeepSeek 基础 URL。"""
        return self.ai.deepseek_base_url

    @property
    def vision_api_key(self) -> Optional[str]:
        """获取火山引擎 API Key。"""
        return os.getenv("VISION_API_KEY") or self.ai.vision_api_key

    @property
    def vision_model(self) -> str:
        """获取火山引擎视觉模型名称。"""
        return self.ai.vision_model

    @property
    def vision_text_model(self) -> str:
        """获取火山引擎文本模型名称。"""
        return self.ai.vision_text_model

    @property
    def vision_base_url(self) -> str:
        """获取火山引擎基础 URL。"""
        return self.ai.vision_base_url

    @property
    def openai_api_key(self) -> Optional[str]:
        """获取 OpenAI API Key。"""
        return os.getenv("OPENAI_API_KEY") or self.ai.openai_api_key

    # --- PDF 便捷属性 ---

    @property
    def enable_pdf_multimodal(self) -> bool:
        """获取是否开启 PDF 多模态解析。"""
        return self.ai.enable_pdf_multimodal

    @property
    def pdf_mode(self) -> str:
        """获取 PDF 解析模式。"""
        return self.ai.pdf_mode

    @property
    def pdf_table_strategy(self) -> str:
        """获取 PDF 表格解析策略。"""
        return self.ai.pdf_table_strategy

    @property
    def pdf_extract_images(self) -> bool:
        """获取是否提取 PDF 图像。"""
        return self.ai.pdf_extract_images

    @property
    def pdf_max_cache_size(self) -> int:
        """获取 PDF 最大缓存条目数。"""
        return self.ai.pdf_max_cache_size

    # --- 日志便捷属性 ---

    @property
    def log_level(self) -> str:
        """获取日志级别。"""
        return self.logging.log_level

    # --- 安全便捷属性 ---

    @property
    def api_key(self) -> Optional[str]:
        """获取 API 认证密钥。"""
        return self.security.api_key

    @property
    def cors_origins_list(self) -> list[str]:
        """将 CORS 来源字符串解析为列表。"""
        return [o.strip() for o in self.security.cors_origins.split(",") if o.strip()]

    @property
    def rate_limit_per_minute(self) -> int:
        """获取每分钟速率限制。"""
        return self.security.rate_limit_per_minute

    # --- 服务器便捷属性 ---

    @property
    def server_host(self) -> str:
        """获取服务器主机地址。"""
        return self.server.host

    @property
    def server_port(self) -> int:
        """获取服务器端口。"""
        return self.server.port

    @property
    def server_workers(self) -> int:
        """获取工作进程数。"""
        return self.server.workers

    def to_environment_dict(self) -> dict[str, str]:
        """将配置转换为环境变量字典。"""
        return {
            "DEEPSEEK_API_KEY": self.deepseek_api_key or "",
            "DEEPSEEK_BASE_URL": self.deepseek_base_url,
            "DEEPSEEK_MODEL": self.deepseek_model,
            "VISION_API_KEY": self.vision_api_key or "",
            "VISION_BASE_URL": self.vision_base_url,
            "VISION_MODEL": self.vision_model,
            "VISION_TEXT_MODEL": self.vision_text_model,
            "OPENAI_API_KEY": self.openai_api_key or "",
            "ENABLE_PDF_MULTIMODAL": str(self.enable_pdf_multimodal),
            "PDF_MODE": self.pdf_mode,
            "PDF_TABLE_STRATEGY": self.pdf_table_strategy,
            "PDF_EXTRACT_IMAGES": str(self.pdf_extract_images),
            "PDF_MAX_CACHE_SIZE": str(self.pdf_max_cache_size),
            "LOG_LEVEL": self.log_level,
            "API_KEY": self.api_key or "",
            "CORS_ORIGINS": self.security.cors_origins,
            "RATE_LIMIT_PER_MINUTE": str(self.rate_limit_per_minute),
        }

    def apply_to_environment(self) -> None:
        """将配置应用到当前进程的环境变量。"""
        for key, value in self.to_environment_dict().items():
            if value:
                os.environ[key] = value


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）。"""
    return Settings()


# 全局配置实例
settings = get_settings()
