

'''
通过“少样本示例”，增加“信息提取能力”
'''
import os
from typing import Optional, List

from langchain_classic.chains.constitutional_ai.prompts import examples
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.utils.function_calling import tool_example_to_messages
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

#定义模型
#deepseek-v4-flash默认开启思考模式，思考模式不支持强制tool_choice，这里显式关闭
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}},
)

#定义结构化输出格式
class people(BaseModel):
    name: Optional[str] = Field(description="这个人的名字",default=None)
    height: Optional[float] = Field(description="这个人的身高",default=None)
    skin: Optional[str]=Field(description="这个人的肤色",default=None)
    age: Optional[int]=Field(description="这个人的年龄",default=None)
    hair_color:Optional[str]=Field(description="这个人的发色",default=None)

#定义最终输出
class Data(BaseModel):
    '''对人特征的提取'''
    person:List[people]
#定义示例:
examples=[
    (
"海洋是⼴阔⽽蓝⾊的。它有两万多英尺深。",
Data(person=[]), # 没有⼈物信息的情况
    ),
    (
"⼩强从中国远⾏到美国。",
Data(person=[
people(name="⼩强", height=None, skin=None,age=None,hair_color=None),
]), # 部分信息缺失的情况
    ),
]

#定义提示词模板
example_prompt=ChatPromptTemplate(
    [
        ("system","你是⼀个提取信息的专家，只从⽂本中提取相关信息.如果您不知道要提取的属性的值，属性值返回null"),
        ("placeholder","{example_messages}"),
        ("human","{conversation}")
    ]
)

#定义少样本提示
# 4. 将示例转换为Messages
example_messages=[]
for txt, tool_call in examples:
    if tool_call.person:
        ai_response = "检测到人"
    else:
        ai_response = "未检测到人"
    example_messages.extend(tool_example_to_messages(
        txt,  # 示例的输入
        [tool_call],  # 工具（ Data(people=[]) 准确的参考标准）
        ai_response=ai_response,  # 让 LLM 强制返回ai_response
    ))


#
#[HumanMessage(content='海洋是⼴阔⽽蓝⾊的。它有两万多英尺深。', additional_kwargs={}, response_metadata={}),
# AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '82c71eca-7c1c-4fb5-916a-d3d5a1678692', 'type': 'function', 'function': {'name': 'Data', 'arguments': '{"person":[]}'}}]}, response_metadata={}, tool_calls=[{'name': 'Data', 'args': {'person': []}, 'id': '82c71eca-7c1c-4fb5-916a-d3d5a1678692', 'type': 'tool_call'}], invalid_tool_calls=[]),
# ToolMessage(content='You have correctly called this tool.', tool_call_id='82c71eca-7c1c-4fb5-916a-d3d5a1678692'),
# AIMessage(content='未检测到人', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content='⼩强从中国远⾏到美国。', additional_kwargs={}, response_metadata={}),
# AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '0a0f5b71-dbc0-49f0-927a-9ff5116bac09', 'type': 'function', 'function': {'name': 'Data', 'arguments': '{"person":[{"name":"⼩强","height":null,"skin":null,"age":null,"hair_color":null}]}'}}]}, response_metadata={}, tool_calls=[{'name': 'Data', 'args': {'person': [{'name': '⼩强', 'height': None, 'skin': None, 'age': None, 'hair_color': None}]}, 'id': '0a0f5b71-dbc0-49f0-927a-9ff5116bac09', 'type': 'tool_call'}], invalid_tool_calls=[]),
# ToolMessage(content='You have correctly called this tool.', tool_call_id='0a0f5b71-dbc0-49f0-927a-9ff5116bac09'),
# AIMessage(content='检测到人', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[])]

# print(example_messages)

#模型调用
#deepseek不支持json_schema格式的response_format，改用function_calling方式
with_struct_model=model.with_structured_output(Data, method="function_calling")
chain= example_prompt | with_struct_model

print(chain.invoke({"example_messages": example_messages,
                    "conversation": "篮球场上，⾝⾼两⽶的中锋王伟默契地将球传给⼀⽶七的后卫挚友李明，完成⼀记绝杀。这对⽼友⽤⼗年配合弥补了⾝⾼的差距。"}))

