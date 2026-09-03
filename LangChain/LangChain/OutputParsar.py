
'''
关于输出解析器的代码运用
'''
import os
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

#定义模型
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#定义消息问题

#定义结构化的输出格式
#定义Pydantic的结构化输出“对象”
class knowledge(BaseModel):
    setup: str=Field(description="这是这个小知识的摘要")
    core: str=Field(description="这是这个小知识的核心内容")
    rating: Optional[int]=Field(description="这是这个小知识的冷门程度，从1-10打分")

#定义输出解析器(对象输出解析器)
# Parser=PydanticOutputParser(pydantic_object=knowledge)

#定义输出解析器（JSON输出解析器）
Parser=JsonOutputParser(pydantic_object=knowledge)

#定义提示词模板
# propmt_template=PromptTemplate(
#     template="根据用户的问题进行回答,返回结构说明：{format_structer},用户问题:{query}",
#     partial_variables={"format_structer":Parser.get_format_instructions()},
#     input_variables=["query"]
# )


#定义链
chain= model | Parser
# chain=propmt_template | model | Parser
# print(chain.invoke({"query": "给我一个关于电脑设备使用相关的小知识"}))
print(chain.invoke("给我简短的介绍一个有用的小知识，以JSON格式输出，"
     "JSON必须包含以下字段：setup(这个小知识的摘要)、"
     "core(这个小知识的核心内容)、rating(这个小知识的冷门程度，从1-10打分)"))