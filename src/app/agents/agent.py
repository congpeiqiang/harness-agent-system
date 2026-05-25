"""
@File    :  agent.py
@Author  :  CongPeiQiang
@Time    :  2026/5/21 14:09
@Desc    :  
"""
# pip install -qU langchain "langchain[openai]"
from langchain.agents import create_agent

from dotenv import load_dotenv
from langchain.agents.middleware import before_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
import os
from app.middleware.pdf_parse_middleware import PDFParseMiddleware
from app.tools import parse_pdf_from_file, parse_pdf_from_content, parse_pdf_from_url
from langchain.chat_models import init_chat_model
load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@before_model
def print_hook(state: AgentState, runtime: Runtime):
    print("Before calling model")
    print(state)
    return state

model = init_chat_model(os.getenv("VISION_MODEL"), model_provider=os.getenv("VISION_MODEL_PROVIDER"), api_key=os.getenv("VISION_API_KEY"), base_url=os.getenv("VISION_BASE_URL"))

agent = create_agent(
    model=model,
    tools=[get_weather, parse_pdf_from_file, parse_pdf_from_content, parse_pdf_from_url],
    system_prompt="You are a helpful assistant",
    middleware=[print_hook, PDFParseMiddleware()]
)

# result = agent.invoke(
#     {"messages": [{"role": "user", "content": r"What's the weather in San Francisco?, 解析 D:\workspace\huice_008\harness-agent-system\src\app\resources\旅行日记.pdf"}]}
# )
# print(result["messages"][-1].content_blocks)
