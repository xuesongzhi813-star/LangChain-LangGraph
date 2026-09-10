import os
from dataclasses import dataclass
from typing import Callable, TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, dynamic_prompt
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

#定义模型
model = ChatOpenAI(model="deepseek-v4-flash", api_key=os.getenv("DEEPSEEK_API_KEY"),
                   base_url="https://api.deepseek.com")


#上下文构造
#给上下文中，提供新的存储属性
class Context(TypedDict):
    the_role: str

#使用override的方式
@wrap_model_call
def new_system_prompt(
        request: ModelRequest,
        handler:Callable[[ModelRequest],ModelResponse],
)->ModelResponse:
    base_prompt="你是一名资深专家"
    user_role=request.runtime.context.get("the_role","初学者")
    if user_role == "初学者":
        system_prompt=list(base_prompt)+[{"type":"text","text":"请用清晰，简洁易懂的话语介绍，尽量少涉及专业用语"}]
        prompt=SystemMessage(content=system_prompt)
        request.override(system_message=prompt)
    elif user_role == "专家":
        system_prompt=list(base_prompt)+[{"type":"text","text":"请用专业的知识，解释清楚"}]
        prompt = SystemMessage(content=system_prompt)
        request.override(system_message=prompt)
    return handler(request)


#使用专属注解@dynamic_prompt实现
# @dynamic_prompt
# def new_system_prompt(request: ModelRequest) -> str:
#     #通过“上下文”去取到，用户的身份，从而定制“动态提示词”
#     user_role = request.runtime.context.get("the_role","初学者")
#     base_prompt = "你是一位资深专家"
#     if user_role == "初学者":
#         return f"{base_prompt},请用清晰，简洁易懂的话语介绍，尽量少涉及专业用语"
#     elif user_role == "专家":
#         return f"{base_prompt},请用专业的知识，解释清楚"
#     return base_prompt


#通过@dynamic_prompt注解实现
# agent = create_agent(
#     model=model,
#     middleware=[new_system_prompt],
#     context_schema=Context,
# )

#
agent=create_agent(
    model=model,
    middleware=[new_system_prompt],
    context_schema=Context,
)
#注意：context_schema 定义的上下文，必须通过 invoke 的 context 参数传入，
#不能混入 state 输入字典中，否则 runtime.context 为 None
response = agent.invoke(
    {"messages": [{"role": "user", "content": "解释一下，什么是机器学习?"}]},
    context={"the_role": "初学者"},
)
print(response)
