"""Test suite for Harness Agent System."""

import pytest


@pytest.fixture(autouse=True)
def _setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("VISION_API_KEY", "test-key")
    monkeypatch.setenv("VISION_MODEL", "doubao-seed-1-6-vision-250815")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_KEY", "test-api-key")
