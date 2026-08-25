import os

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, filter_messages
from langchain_openai import ChatOpenAI

#定义模型
# model=ChatOpenAI(
#     base_url="https://api.deepseek.com",
#     model="deepseek-v4-flash",
#     api_key=os.getenv("DEEPSEEK_API_KEY")
# )

# 历史消息记录
messages = [
SystemMessage("你是一个聊天助手", id="1"),
HumanMessage("示例输入", id="2"),
AIMessage("示例输出", id="3"),
HumanMessage("真实输入", id="4"),
AIMessage("真实输出", id="5"),
]

#过滤消息（按照“消息类型”过滤），得到指定的结果
# Filter=filter_messages(
#     messages=messages,
#     include_types="human"#/exclude排除
# )
# #[HumanMessage(content='示例输入', additional_kwargs={}, response_metadata={}, id='2'),
# # HumanMessage(content='真实输入', additional_kwargs={}, response_metadata={}, id='4')]
# print(Filter)

#过滤消息（按照id过滤）
Filter=filter_messages(
    messages=messages,
    exclude_ids="1"
)


#[HumanMessage(content='示例输入', additional_kwargs={}, response_metadata={}, id='2'),
# AIMessage(content='示例输出', additional_kwargs={}, response_metadata={}, id='3', tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content='真实输入', additional_kwargs={}, response_metadata={}, id='4'),
# AIMessage(content='真实输出', additional_kwargs={}, response_metadata={}, id='5', tool_calls=[], invalid_tool_calls=[])]
print(Filter)





