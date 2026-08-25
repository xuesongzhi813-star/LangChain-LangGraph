import os
from typing import Optional, Union

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, RootModel


#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#使用Pydanic对象的方式定义结构化输出格式
class knowledge(BaseModel):
    """一个有用知识的介绍"""
    setup: str=Field(description="这是这个小知识的摘要")
    core: str=Field(description="这是这个小知识的核心内容")
    rating: Optional[int]=Field(description="这是这个小知识的冷门程度，从1-10打分")

#另一个结构化输出
class responses(BaseModel):
    """正常的回复用户"""
    content: str=Field(description="这是对用户常规提问的回答")

#对两个结构化输出的总和：让LLM根据问题自行选择输出其中一种结构
#用RootModel联合类型，模型直接返回其中一种结构，无需外层包装
class select(RootModel[Union[knowledge,responses]]):
    """这是LLM根据问题类型选择的最终结构化输出"""

#绑定结构化输出
#DeepSeek只支持json_mode；且json_mode不会把schema传给模型，
#所以用提示词描述"final_select"包装结构和两种候选结构，让LLM根据问题类型自选
model_with_structured=model.with_structured_output(select, method="json_mode")

#统一的路由提示词：模型自己判断问题类型并选择输出结构
ROUTER_PROMPT=(
    "根据我提问的类型，自动选择合适的JSON结构回答，二选一：\n"
    "1) 问题是要介绍/讲解一个小知识时，输出："
    '{{"setup": 摘要, "core": 核心内容, "rating": 冷门程度(1-10的整数)}}\n'
    "2) 问题是普通对话/常规提问时，输出："
    '{{"content": 对这个问题的回答}}\n'
    "只能输出其中一种，不要添加其他字段。问题：{question}")

#进行多问题调用
print(model_with_structured.invoke(ROUTER_PROMPT.format(question="给我简短介绍一个有用的小知识")))
print(model_with_structured.invoke(ROUTER_PROMPT.format(question="你是谁")))