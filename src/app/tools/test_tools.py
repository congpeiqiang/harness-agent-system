"""Test tools: weather query (sync & async) and file reading."""

import asyncio
from typing import Optional

import aiohttp
import requests
from langchain_core.tools import tool


def _get_coordinates(city: str) -> Optional[tuple[float, float]]:
    """Resolve city name to (latitude, longitude) via Open-Meteo Geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "zh", "format": "json"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None
        return (results[0]["latitude"], results[0]["longitude"])
    except Exception:
        return None


async def _get_coordinates_async(city: str) -> Optional[tuple[float, float]]:
    """Async resolve city name to (latitude, longitude)."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "zh", "format": "json"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                results = data.get("results", [])
                if not results:
                    return None
                return (results[0]["latitude"], results[0]["longitude"])
    except Exception:
        return None


@tool
def get_weather(location: str) -> str:
    """Query the current weather for a given city/location.

    Args:
        location: City name or location description (e.g. "Beijing", "Shanghai", "Wuxi").

    Returns:
        A human-readable weather summary string.
    """
    coords = _get_coordinates(location)
    if coords is None:
        return f"Unable to find coordinates for '{location}'. Please check the location name."

    lat, lon = coords
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    try:
        resp = requests.get(weather_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind = current.get("wind_speed_10m", "N/A")
        code = current.get("weather_code", -1)

        # WMO Weather interpretation codes (0-99)
        weather_map = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            56: "Light freezing drizzle", 57: "Dense freezing drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            66: "Light freezing rain", 67: "Heavy freezing rain",
            71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
        }
        weather_desc = weather_map.get(code, "Unknown")

        return (
            f"Weather in {location}: {weather_desc}. "
            f"Temperature: {temp}°C, Humidity: {humidity}%, Wind speed: {wind} km/h."
        )
    except Exception as e:
        return f"Failed to fetch weather for '{location}': {e}"


@tool
async def get_weather_async(location: str) -> str:
    """Asynchronously query the current weather for a given city/location.

    Args:
        location: City name or location description (e.g. "Beijing", "Shanghai", "Wuxi").

    Returns:
        A human-readable weather summary string.
    """
    coords = await _get_coordinates_async(location)
    if coords is None:
        return f"Unable to find coordinates for '{location}'. Please check the location name."

    lat, lon = coords
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                current = data.get("current", {})
                temp = current.get("temperature_2m", "N/A")
                humidity = current.get("relative_humidity_2m", "N/A")
                wind = current.get("wind_speed_10m", "N/A")
                code = current.get("weather_code", -1)

                weather_map = {
                    0: "Clear sky",
                    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                    45: "Fog", 48: "Depositing rime fog",
                    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
                    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                    66: "Light freezing rain", 67: "Heavy freezing rain",
                    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                    77: "Snow grains",
                    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                    85: "Slight snow showers", 86: "Heavy snow showers",
                    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
                }
                weather_desc = weather_map.get(code, "Unknown")

                return (
                    f"Weather in {location}: {weather_desc}. "
                    f"Temperature: {temp}°C, Humidity: {humidity}%, Wind speed: {wind} km/h."
                )
    except Exception as e:
        return f"Failed to fetch weather for '{location}': {e}"


@tool
def read_file(filepath: str) -> str:
    """Read and return the contents of a local text file.

    Args:
        filepath: Absolute or relative path to the file.

    Returns:
        The file contents as a string, or an error message if the file cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read file '{filepath}': {e}"