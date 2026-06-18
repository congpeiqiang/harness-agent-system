"""
天气工具测试。

测试天气查询工具的同步和异步功能。
"""

import pytest
from app.tools.weather_tool import get_weather, get_weather_async


class TestWeatherTool:
    """天气工具测试。"""

    def test_get_weather_beijing(self):
        """测试北京天气查询。"""
        result = get_weather.invoke({"city": "北京"})
        assert "北京" in result
        assert "°C" in result

    def test_get_weather_shanghai(self):
        """测试上海天气查询。"""
        result = get_weather.invoke({"city": "上海"})
        assert "上海" in result
        assert "°C" in result

    def test_get_weather_new_york(self):
        """测试纽约天气查询。"""
        result = get_weather.invoke({"city": "New York"})
        assert "New York" in result

    def test_get_weather_unknown_city(self):
        """测试未知城市查询。"""
        result = get_weather.invoke({"city": "未知城市"})
        assert "暂未收录" in result

    def test_get_weather_case_insensitive(self):
        """测试大小写不敏感查询。"""
        result = get_weather.invoke({"city": "beijing"})
        assert "北京" in result

    @pytest.mark.asyncio
    async def test_get_weather_async(self):
        """测试异步天气查询。"""
        result = await get_weather_async.ainvoke({"city": "北京"})
        assert "北京" in result
        assert "°C" in result

    @pytest.mark.asyncio
    async def test_get_weather_async_unknown(self):
        """测试异步未知城市查询。"""
        result = await get_weather_async.ainvoke({"city": "未知城市"})
        assert "暂未收录" in result
