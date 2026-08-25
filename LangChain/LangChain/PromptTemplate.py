import os

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#一般来说，与AI对话要求对于同一类型问题的会话，可以采取：提示词模板+输入变量

#文本处理型，提示词模板
#方式一：
# prompt_template=PromptTemplate(
#     template="给我介绍一下{city}的景点，3个",
#     input_variables="{city}"
# )
#
# while(True):
#     city=input("\n 请输入你想了解的城市,如果要退出输入:quit \n")
#     if city=="quit":
#         break
#         #这只是组装好了完成的提示词，使用invoke/format
#     # print(PromptTemplate.format(
#     #     prompt_template,
#     #     city=city))
#     #使用invoke也行，因为本质是一个runnable实例，需要invoke/format成messages
#     print(prompt_template.invoke(
#         city
#     ))
#     #真正调用提示词
#     model.invoke(PromptTemplate.format(
#         prompt_template,
#         city=city)).pretty_print()
#
#文本类型提示模板
#方式二：
# prompt_template=PromptTemplate().from_template(
#     template="请你介绍这个{city}的景点，3个"
#
# )
#
# while True:
#     city=input("\n 请输入你想了解的城市 输入quit代表退出\n")
#     if city=="quit":
#         break
#     # 实例化为messages
#     print(prompt_template.invoke({"city": city}))
#     #执行
#     model.invoke(prompt_template)

#聊天消息提示词模板
#因为是处理“聊天”的提示词模板，因此也采取messages类似的写模板（例：systemMessage）
#通过“占位符”实现附加上下文
prompt_template=ChatPromptTemplate(
    #这个[]相当于是message骨架
    [
    ("system","请帮助我从 {input_form} 翻译成 {input_to} "),
    ("placeholder","{conversation}"),
    ("human","{text}")
    ]

)

#实例化成“messages”
#按照字典的形式
messages=prompt_template.invoke({
    "input_form": "中文",
    "input_to": "英文",
    "text": "浮沉",
    #conversation中就是历史对话“上下文”
    "conversation":[
    ("human","苹果"),
    ("ai","apple"),
    ("human","扶摇直上九万里"),]
})

#messages=[SystemMessage(content='请帮助我从 中文 翻译成 英文 ', additional_kwargs={}, response_metadata={}),
# HumanMessage(content='苹果', additional_kwargs={}, response_metadata={}),
# AIMessage(content='apple', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content='扶摇直上九万里', additional_kwargs={}, response_metadata={}),
# HumanMessage(content='浮沉', additional_kwargs={}, response_metadata={})]
print(messages)
#交给模型执行
model.invoke(messages).pretty_print()
