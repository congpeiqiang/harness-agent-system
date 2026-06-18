"""
@File    :  agent.py
@Author  :  CongPeiQiang
@Time    :  2026/5/21 20:09
@Desc    :  Agent factory with pluggable checkpointer / store.
"""
import time

from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain.agents.middleware import before_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
import os
from watchfiles import awatch
from app.middleware.pdf_parse_middleware import PDFParseMiddleware
from langchain.agents.middleware import HumanInTheLoopMiddleware, ToolCallLimitMiddleware, SummarizationMiddleware, ModelFallbackMiddleware
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware.skills import SkillsMiddleware
from app.tools import parse_pdf_from_file, parse_pdf_from_content, parse_pdf_from_url
from app.tools import get_weather, read_file, get_weather_async
from langchain.chat_models import init_chat_model
from app.tools.mcp_client_builder import get_mcp_tools_async
from langgraph.types import Command
import asyncio
from app.core.state import CustomState, ContextState

load_dotenv()


@before_model
def print_hook(state: AgentState, runtime: Runtime):
    print("Before calling model")
    print(state)
    execution_info = getattr(runtime, "execution_info", None)
    server_info = getattr(runtime, "server_info", None)
    if execution_info:
        thread_id = getattr(execution_info, "thread_id", "unknown")
    else:
        thread_id = "unknown"
    if server_info:
        assistant_id = getattr(server_info, "assistant_id", "unknown")
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
    ToolCallLimitMiddleware(
        tool_name="get_weather_async",
        thread_limit=20,
        run_limit=3
    ),
    # ToolCallLimitMiddleware(
    #     tool_name="get_weather",
    #     thread_limit=20,
    #     run_limit=3
    # )
]

model = init_chat_model(
    os.getenv("DEEPSEEK_MODEL"),
    model_provider=os.getenv("DEEPSEEK_MODEL_PROVIDER"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

backend = FilesystemBackend(
    root_dir="/code_work_space/llm/huice/008/harness-agent-system/src/app/workspace/skills",
    virtual_mode=True
)
skillsMiddleware = SkillsMiddleware(
    backend=backend,
    sources=["./fecmall_skills"],
)

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.sqlite import AsyncSqliteStore

async def async_init_checkpointer_store():
    import aiosqlite
    # 方式二: 直接初始化（需要手动管理连接）
    conn = await aiosqlite.connect(r"D:\code_work_space\llm\huice\008\harness-agent-system\checkpoints.sqlite")
    saver = AsyncSqliteSaver(conn)
    store = AsyncSqliteStore(conn)
    return saver, store

# 等待 MCP 工具初始化完成
def get_all_tools():
    tools = [
        get_weather,
        parse_pdf_from_file,
        parse_pdf_from_content,
        parse_pdf_from_url
    ]
    mcp_tools = asyncio.run(get_mcp_tools_async())
    tools.extend(mcp_tools)
    return tools

async def get_all_tools_async():
    tools = [
        get_weather,
        parse_pdf_from_file,
        parse_pdf_from_content,
        parse_pdf_from_url
    ]
    # mcp_tools = asyncio.run(get_mcp_tools_async())
    mcp_tools = await get_mcp_tools_async()
    tools.extend(mcp_tools)
    return tools


# tools = get_all_tools()
#
# agent = create_agent(
#         model=model,
#         state_schema=CustomState,
#         context_schema=ContextState,
#         tools=tools,
#         system_prompt="You are a helpful assistant",
#         middleware=[
#             print_hook,
#             PDFParseMiddleware(),
#             ModelFallbackMiddleware(os.getenv("DEEPSEEK_MODEL"), os.getenv("DEEPSEEK_MODEL")),
#             *humanInTheLoopMiddleware,
#             *toolCallLimitMiddleware
#         ]
#     )




async def build_agent(checkpointer, store):
    """Build and return an agent instance with the given persistence layers."""
    tools = await  get_all_tools_async()
    return create_agent(
        model=model,
        state_schema=CustomState,
        context_schema=ContextState,
        tools=tools,
        system_prompt="You are a helpful assistant",
        middleware=[
            print_hook,
            PDFParseMiddleware(),
            ModelFallbackMiddleware(os.getenv("DEEPSEEK_MODEL"), os.getenv("DEEPSEEK_MODEL")),
            *humanInTheLoopMiddleware,
            *toolCallLimitMiddleware
        ],
        checkpointer=checkpointer,
        store=store,
    )


async def astream_demo():
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.store.memory import InMemoryStore

    cp = MemorySaver()
    st = InMemoryStore()
    agent = await build_agent(cp, st)
    config = {"configurable": {"thread_id": "thread_id-111"}}
    async for chunk in agent.astream(
        # {"messages": [{"role": "user", "content": r"登录fecmall, email是1539397036@qq.com, password是123456"}]},
        {"messages": [{"role": "user", "content": r"无锡天气？"}]},
        config=config,
        context=ContextState(
                    user_id="user_id_111",
                    thread_id="thread_id_111",
                ),
        stream_mode="values",
        version="v2"
    ):
        print(chunk)
        if "__interrupt__" in chunk["data"]:
            print(chunk["data"]["__interrupt__"])


if __name__ == '__main__':
    # from langgraph.checkpoint.memory import MemorySaver
    # from langgraph.store.memory import InMemoryStore
    #
    # cp = MemorySaver()
    # st = InMemoryStore()
    # agent = build_agent(cp, st)

    # result = agent.ainvoke(
    #     {
    #         "messages": [{"role": "user", "content": r"无锡天气?"}],
    #         "question":"无锡天气?"
    #     },
    #     config={"configurable": {"thread_id": "thread_id_111"}},
    #     context=ContextState(
    #         user_id="user_id_111",
    #         thread_id="thread_id_111",
    #     )
    # )
    # print("======result======")
    # print(result)
    # for msg in result["messages"]:
    #     msg.pretty_print()

    asyncio.run(astream_demo())
