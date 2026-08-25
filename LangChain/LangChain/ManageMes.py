import os

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_openai import ChatOpenAI

from LangChain.test1 import messages

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#通过裁剪的方式管理消息列表
#(1)按照token数裁剪
messages=[
SystemMessage(content="you're a good assistant"),
HumanMessage(content="hi! I'm bob"),
AIMessage(content="hi!"),
HumanMessage(content="I like vanilla ice cream"),
AIMessage(content="nice"),
HumanMessage(content="whats 2 + 2"),
AIMessage(content="4"),
HumanMessage(content="thanks"),
AIMessage(content="no problem!"),
HumanMessage(content="having fun?"),
AIMessage(content="yes!"),
HumanMessage(content="What's my name?"),
]
#
# #先调用观察结果
# print(model.invoke(messages))
#按照token裁剪
#注意：token计数只支持gpt
# Trim=trim_messages(
#     #更多参数，可以查看官方文档
#     messages=messages,#需要裁剪的消息
#     max_tokens=140,#裁剪出的消息的“token数”
#     token_counter=model,#传入一个函数/LLM，因为LLM是按照token计数
#     strategy="last",#裁剪策略，保留最新的消息（如果超出token，就把老的消息裁剪）
#     start_on="human",#起始的“消息类型”
#     include_system=True,#始终保留初始系统消息（即SystemMessage）
#     allow_partial=False#是否允许拆分消息的内容
# )

#按照消息数裁剪
Trim=trim_messages(
    messages=messages,
    token_counter=len,#传入len函数本身-->统计消息条数（不能写len(messages)，那会直接算出int）
    max_tokens=10,
    strategy="last",#裁剪策略，保留最新的消息（如果超出token，就把老的消息裁剪）
    start_on="human",#起始的“消息类型”
    include_system=True,#始终保留初始系统消息（即SystemMessage）
    allow_partial=False#是否允许拆分消息的内容
)

#[SystemMessage(content="you're a good assistant", additional_kwargs={}, response_metadata={}),
# HumanMessage(content='I like vanilla ice cream', additional_kwargs={}, response_metadata={}),
# AIMessage(content='nice', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='whats 2 + 2', additional_kwargs={}, response_metadata={}),
# AIMessage(content='4', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content='thanks', additional_kwargs={}, response_metadata={}),
# AIMessage(content='no problem!', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content='having fun?', additional_kwargs={}, response_metadata={}),
# AIMessage(content='yes!', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content="What's my name?", additional_kwargs={}, response_metadata={})]
#裁剪消息验证
print(Trim)

#定义链，先裁剪了消息，再交给LLM调用
#注意：langchain_core 1.x 里 trim_messages 是普通函数，调用后直接返回裁剪好的消息列表，
#并不是 Runnable，所以不能用 Trim | model 组链（list 不支持 | 管道）。
#直接把裁剪后的消息列表交给模型调用即可。
result=model.invoke(Trim)
print(result)