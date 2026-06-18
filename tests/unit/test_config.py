"""
配置模块测试。

测试 Settings 类的默认值、验证和环境变量加载。
"""

import pytest
from app.core.config import Settings, get_project_root


class TestSettings:
    """Settings 类测试。"""

    def test_settings_loads_defaults(self):
        """测试默认配置加载。"""
        s = Settings()
        assert s.ai.deepseek_model == "deepseek-chat"
        # 注意：conftest.py 中 monkeypatch 将 LOG_LEVEL 设置为 DEBUG
        assert s.logging.log_level in ("INFO", "DEBUG")

    def test_log_level_validation(self):
        """测试日志级别验证。"""
        with pytest.raises(ValueError):
            Settings(logging={"log_level": "INVALID"})

    def test_security_settings(self):
        """测试安全相关配置。"""
        s = Settings()
        assert isinstance(s.security.cors_origins, str)
        assert s.security.rate_limit_per_minute > 0

    def test_project_root(self):
        """测试项目根目录获取。"""
        root = get_project_root()
        assert root.exists()
        assert (root / "pyproject.toml").exists()
