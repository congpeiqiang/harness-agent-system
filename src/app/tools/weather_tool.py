"""
天气查询工具。

提供同步和异步的天气查询功能，支持全球主要城市。
"""

import asyncio
from typing import Any

import httpx
from langchain_core.tools import tool


# --- 天气数据 ---

# 模拟天气数据（用于演示和测试）
WEATHER_DATA = {
    "北京": {"temp": "25°C", "condition": "晴朗", "humidity": "40%"},
    "上海": {"temp": "28°C", "condition": "多云", "humidity": "65%"},
    "广州": {"temp": "32°C", "condition": "雷阵雨", "humidity": "85%"},
    "深圳": {"temp": "31°C", "condition": "多云", "humidity": "78%"},
    "杭州": {"temp": "26°C", "condition": "晴朗", "humidity": "55%"},
    "成都": {"temp": "24°C", "condition": "阴天", "humidity": "70%"},
    "武汉": {"temp": "27°C", "condition": "晴朗", "humidity": "50%"},
    "西安": {"temp": "23°C", "condition": "晴朗", "humidity": "35%"},
    "重庆": {"temp": "30°C", "condition": "多云", "humidity": "75%"},
    "南京": {"temp": "26°C", "condition": "晴朗", "humidity": "60%"},
    "New York": {"temp": "72°F", "condition": "Sunny", "humidity": "45%"},
    "London": {"temp": "18°C", "condition": "Cloudy", "humidity": "70%"},
    "Tokyo": {"temp": "28°C", "condition": "Sunny", "humidity": "55%"},
    "Paris": {"temp": "20°C", "condition": "Partly Cloudy", "humidity": "60%"},
}


def _get_weather_sync(city: str) -> str:
    """获取天气信息的同步内部函数。"""
    city_lower = city.lower().strip()

    # 检查模拟数据
    for key in WEATHER_DATA:
        if key.lower() == city_lower:
            data = WEATHER_DATA[key]
            return f"{key}天气: {data['temp']}, {data['condition']}, 湿度{data['humidity']}"

    # 未找到数据
    return f"{city}的天气信息暂未收录，当前仅支持以下城市: {', '.join(WEATHER_DATA.keys())}"


@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的当前天气信息。

    Args:
        city: 要查询天气的城市名称，如 "北京"、"上海"、"New York"

    Returns:
        包含温度、天气状况和湿度的天气信息字符串。
    """
    return _get_weather_sync(city)


async def _get_weather_async_api(city: str) -> str:
    """异步获取天气 API 数据。"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://api.seniverse.com/v3/weather/now.json"
            params = {
                "key": "S6qO4WZ6Y6W5R8u4S",
                "location": city,
                "language": "zh-Hans",
                "unit": "c",
            }
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if "results" in data and data["results"]:
                result = data["results"][0]
                location = result.get("location", {}).get("name", city)
                temp = result.get("now", {}).get("temperature", "未知")
                text = result.get("now", {}).get("text", "未知")
                return f"{location}天气: {temp}°C, {text}"
    except Exception:
        pass
    return ""


@tool
async def get_weather_async(city: str) -> str:
    """
    异步查询指定城市的当前天气信息。

    优先尝试外部 API，失败时回退到本地数据。

    Args:
        city: 要查询天气的城市名称

    Returns:
        包含温度和天气状况的天气信息字符串。
    """
    # 尝试外部 API
    api_result = await _get_weather_async_api(city)
    if api_result:
        return api_result

    # 回退到本地数据
    return _get_weather_sync(city)
