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
from app.tools import parse_pdf_from_file, parse_pdf_from_content
load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@before_model
def print_hook(state: AgentState, runtime: Runtime):
    print("Before calling model")
    print(state["messages"])
    return state


agent = create_agent(
    model="deepseek-chat",
    tools=[get_weather, parse_pdf_from_file, parse_pdf_from_content],
    system_prompt="You are a helpful assistant",
    middleware=[print_hook]
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": r"What's the weather in San Francisco?, 解析 D:\code_work_space\icp\intelligent-crystal-pulling\建模-调温&放肩&等径\等径\建模-预测冷热\模型预测冷热\embedding_logistic\data_preprocess\复盘\等径头部功率自动校准复盘文档.pdf"}]}
)
print(result["messages"][-1].content_blocks)