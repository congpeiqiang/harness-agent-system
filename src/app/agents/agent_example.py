"""
@File    :  agent.py
@Author  :  CongPeiQiang
@Time    :  2026/5/20 20:16
@Desc    :  
"""
# deepseek
import os
from langchain.chat_models import init_chat_model
os.environ["DEEPSEEK_API_KEY"] = "sk-9e0e849da2b5495e90b38cf302235cf3"
# model = init_chat_model("deepseek-chat")
# response = model.invoke("Why do parrots talk?")
# print(response)

from langchain_deepseek import ChatDeepSeek
# llm = ChatDeepSeek(
#     model="deepseek-chat",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     # other params...
# )
# response = llm.invoke("Why do parrots talk?")
# print(response.content_blocks)
# print("=====")
# print(response.content)

# # doubao
# os.environ["OPENAI_API_KEY"] = "ark-e8825f80-b0bf-422d-a895-9973de6856b3-c2c33"
# model = init_chat_model("doubao-seed-2-0-lite-260428", model_provider="openai", base_url="https://ark.cn-beijing.volces.com/api/v3")
# response = model.invoke("Why do parrots talk?")
# print(response)

# # kimi
# os.environ["OPENAI_API_KEY"] = "sk-TyFSp2THhYwrWskW4QMVdieM3l5yJe2mgYVezRPFzm8kxiYW"
# model = init_chat_model("kimi-k2.6", model_provider="openai", base_url="https://kimi.a7m.com.cn/v1")
# response = model.invoke("你是谁,请自我介绍?")
# print(response)