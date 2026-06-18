"""Test client for agent RESTful endpoints."""

import json

import requests

BASE_URL = "http://127.0.0.1:2026"


def _build_payload(
    messages: list[dict[str, str]] | None = None,
    thread_id: str = "test-thread",
    user_id: str = "user_1",
) -> dict:
    """Build a common request payload."""
    if messages is None:
        messages = [{"role": "user", "content": "无锡天气？"}]
    return {
        "messages": messages,
        "config": {"configurable": {"thread_id": thread_id}},
        "context": {"user_id": user_id, "thread_id": thread_id},
    }


def test_invoke() -> None:
    """Test POST /agent/invoke."""
    url = f"{BASE_URL}/agent/invoke"
    payload = _build_payload(thread_id="test-invoke-1")
    resp = requests.post(url, json=payload, timeout=120)
    print(f"invoke status: {resp.status_code}")
    try:
        print(f"invoke response: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    except Exception:
        print(f"invoke text: {resp.text}")


def test_ainvoke() -> None:
    """Test POST /agent/ainvoke."""
    url = f"{BASE_URL}/agent/ainvoke"
    payload = _build_payload(thread_id="test-ainvoke-1")
    resp = requests.post(url, json=payload, timeout=120)
    print(f"ainvoke status: {resp.status_code}")
    try:
        print(f"ainvoke response: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    except Exception:
        print(f"ainvoke text: {resp.text}")


def test_stream() -> None:
    """Test POST /agent/stream (SSE)."""
    url = f"{BASE_URL}/agent/stream"
    payload = _build_payload(thread_id="test-stream-1")
    resp = requests.post(url, json=payload, stream=True, timeout=120)
    print(f"stream status: {resp.status_code}")
    for line in resp.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            print(f"  stream chunk: {decoded}")


def test_astream() -> None:
    """Test POST /agent/astream (SSE)."""
    url = f"{BASE_URL}/agent/astream"
    payload = _build_payload(thread_id="test-astream-1")
    resp = requests.post(url, json=payload, stream=True, timeout=120)
    print(f"astream status: {resp.status_code}")
    for line in resp.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            print(f"  astream chunk: {decoded}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing /agent/invoke")
    print("=" * 60)
    test_invoke()

    print("=" * 60)
    print("Testing /agent/ainvoke")
    print("=" * 60)
    test_ainvoke()

    print("=" * 60)
    print("Testing /agent/stream")
    print("=" * 60)
    test_stream()

    print("=" * 60)
    print("Testing /agent/astream")
    print("=" * 60)
    test_astream()
