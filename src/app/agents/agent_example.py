"""
Agent example scripts for testing LLM models.

This file provides example code for testing different LLM providers.
DO NOT store API keys in this file - always use environment variables.

Usage:
    export DEEPSEEK_API_KEY=your_key_here
    python -m app.agents.agent_example
"""

import os
from dotenv import load_dotenv

load_dotenv()


def test_deepseek():
    """Test DeepSeek model."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set")
        return

    from langchain.chat_models import init_chat_model

    model = init_chat_model("deepseek-chat")
    response = model.invoke("Why do parrots talk?")
    print(f"DeepSeek response: {response.content}")


def test_doubao():
    """Test Doubao/Volcano Engine model."""
    api_key = os.getenv("VISION_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: VISION_API_KEY or OPENAI_API_KEY not set")
        return

    from langchain.chat_models import init_chat_model

    model = init_chat_model(
        "doubao-seed-2-0-lite-260428",
        model_provider="openai",
        base_url=os.getenv("VISION_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
    )
    response = model.invoke("Why do parrots talk?")
    print(f"Doubao response: {response.content}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test LLM models")
    parser.add_argument("--model", choices=["deepseek", "doubao"], default="deepseek", help="Model to test")
    args = parser.parse_args()

    if args.model == "deepseek":
        test_deepseek()
    elif args.model == "doubao":
        test_doubao()
