"""
@File    :  agent.py
@Author  :  CongPeiQiang
@Time    :  2026/5/21 20:09
@Desc    :  
"""
# pip install -qU langchain "langchain[openai]"
# from langchain.agents import create_agent
from deepagents import create_deep_agent as create_agent

from dotenv import load_dotenv
from langchain.agents.middleware import before_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
import os
from app.middleware.pdf_parse_middleware import PDFParseMiddleware
from langchain.agents.middleware import HumanInTheLoopMiddleware, ToolCallLimitMiddleware
from app.tools import parse_pdf_from_file, parse_pdf_from_content, parse_pdf_from_url
from langchain.chat_models import init_chat_model
from app.tools.mcp_client_builder import fecmall_tools
from langgraph.types import Command
import asyncio

load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"大到暴雨 {city}!"

@before_model
def print_hook(state: AgentState, runtime: Runtime):
    print("Before calling model")
    print(state)
    # 安全的方式（防止属性不存在）
    execution_info = getattr(runtime, "execution_info", None)
    server_info = getattr(runtime, "server_info", None)
    if execution_info:
        thread_id = getattr(execution_info, "thread_id", "unknown")
    else:
        thread_id = "unknown"
    if server_info:
        assistant_id = getattr(server_info, "assistant_id", "unknown")  # ← 助手ID
    else:
        assistant_id = "unknown"
    print(f"Thread ID: {thread_id}\nAssistant ID: {assistant_id}")
    return state

humanInTheLoopMiddleware = [
        HumanInTheLoopMiddleware(
            interrupt_on={
                "customer_login_submit_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "submit_register_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "paypal_express_start_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "paypal_express_submit_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "paypal_standard_start_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "checkmoney_start_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
            }
        )
    ]

toolCallLimitMiddleware = [
        # Global limit
        # thread_limit:每个线程允许的最大工具调用数。 None 表示没有限制
        # run_limit:每次运行允许的最大工具调用次数。 None 表示没有限制
        ToolCallLimitMiddleware(
            thread_limit=20, run_limit=3
        )
    ]
model = init_chat_model(os.getenv("DEEPSEEK_MODEL"), model_provider=os.getenv("DEEPSEEK_MODEL_PROVIDER"), api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_BASE_URL"))

# 自定义 persistence 组件（需在 start_server.py 中设置 LANGGRAPH_ALLOW_CUSTOM_PERSISTENCE=true）
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

checkpointer = MemorySaver()
store = InMemoryStore()

agent = create_agent(
    model=model,
    tools=[
        get_weather,
        parse_pdf_from_file,
        parse_pdf_from_content,
        parse_pdf_from_url
        ]+fecmall_tools,
    system_prompt="You are a helpful assistant",
    middleware=[print_hook, PDFParseMiddleware()]+humanInTheLoopMiddleware+toolCallLimitMiddleware,
    checkpointer=checkpointer,
    store=store,
)

# result = agent.invoke(
#     {"messages": [{"role": "user", "content": r"What's the weather in San Francisco?, 解析 D:\workspace\huice_008\harness-agent-system\src\app\resources\旅行日记.pdf"}]}
# )

# 人机交互
# config = {"configurable": {"thread_id": "thread_id-111"}}
# result = asyncio.run(agent.ainvoke(
#     {"messages": [{"role": "user", "content": r"登录fecmall, email:1539397036@qq.com, password:123456"}]},
#     config=config,
#     version="v2",
# ))
# print(result.interrupts)
# result = asyncio.run(agent.ainvoke(
#     Command(
#         resume={"decisions": [{"type": "reject"}]}  # or "reject"
#     ),
#     config=config, # Same thread ID to resume the paused conversation
#     version="v2",
# ))
# print(result)
# for msg in result["messages"]:
#     msg.pretty_print()

# async def main():
#     stream = await agent.astream_events(
#         {"messages": [{"role": "user", "content": r"登录fecmall, email是1539397036@qq.com, password是123456"}]},
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
