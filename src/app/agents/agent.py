"""
@File    :  agent.py
@Author  :  CongPeiQiang
@Time    :  2026/5/21 20:09
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
from app.tools.mcp_client_builder import fecmall_tools
import asyncio

load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@before_model
def print_hook(state: AgentState, runtime: Runtime):
    print("Before calling model")
    print(state)
    return state

model = init_chat_model(os.getenv("DEEPSEEK_MODEL"), model_provider=os.getenv("DEEPSEEK_MODEL_PROVIDER"), api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_BASE_URL"))

agent = create_agent(
    model=model,
    tools=[
        get_weather,
        parse_pdf_from_file,
        parse_pdf_from_content,
        parse_pdf_from_url
        ]+fecmall_tools,
    system_prompt="You are a helpful assistant",
    # middleware=[print_hook, PDFParseMiddleware()]
)

# result = agent.invoke(
#     {"messages": [{"role": "user", "content": r"What's the weather in San Francisco?, 解析 D:\workspace\huice_008\harness-agent-system\src\app\resources\旅行日记.pdf"}]}
# )

# result = asyncio.run(agent.ainvoke(
#     {"messages": [{"role": "user", "content": r"登录fecmall, email:1539397036@qq.com, password:123456"}]}
# ))
# for msg in result["messages"]:
#     msg.pretty_print()

# async def main():
#     stream = await agent.astream_events(
#         {"messages": [{"role": "user", "content": r"登录fecmall, email是1539397039@qq.com, password是123456"}]},
#         version="v3")
#
#     async for message in stream.messages:
#         # async for chunk in message.tool_calls:
#         #     print(f"tool call chunk: {chunk}")
#         print("message.text")
#         print(await message.text)
#         print("message.output")
#         print(await message.output)
#
#     async for call in stream.tool_calls:
#         print("stream.tool_calls=====")
#         print(f"{call.tool_name}({call.input})")
#         async for delta in call.output_deltas:
#             print(delta, end="", flush=True)
#         print(call.output, call.error)
#         print("stream.tool_calls=====")
# if __name__ == '__main__':
#     asyncio.run(main())