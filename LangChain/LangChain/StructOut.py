import os
from typing import Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from pydantic import Field, BaseModel

#定义模型
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#定义消息问题

#定义结构化的输出格式
#定义Pydantic的结构化输出“对象”
# class knowledge(BaseModel):
#     setup: str=Field(description="这是这个小知识的摘要")
#     core: str=Field(description="这是这个小知识的核心内容")
#     rating: Optional[int]=Field(description="这是这个小知识的冷门程度，从1-10打分")

#定义结构化的输出格式
#定义TypedDic的字典输出格式
# class knowledge(TypedDict):
#     setup: Annotated[str,...,"这是这个小知识的摘要"]
#     core: Annotated[str,...,"这是这个小知识的核心内容"]
#     rating: Annotated[Optional[int],...,"这是这个小知识的冷门程度，从1-10打分"]


#定义结构化的输出格式
#定义JSON的输出格式
json_schema={
    "title": "knowledge",
    "description": "介绍一个有用的小知识",
    "type": "object",
    "properties": {
        "setup": {
            "type": "string",
            "description": "这是这个小知识的摘要"
        },
        "core": {
            "type": "string",
            "description": "这是这个小知识的核心内容"
        },
        "rating": {
            "type": "integer",
            "description": "这是这个小知识的冷门程度，从1-10打分",
            "default": None
        }
    },
    "required": ["setup", "core"]
}


#绑定结构化输出的“输出格式”(绑定Pydantic对象的输出结构)
#DeepSeek不支持json_schema类型的response_format；function_calling会强制tool_choice，
#而thinking模式又不允许强制tool_choice，所以改用json_mode（response_format=json_object，不设置tool_choice）
# model_with_structured=model.with_structured_output(knowledge, method="json_mode")
# print(model_with_structured.invoke(
#     "给我简短的介绍一个有用的小知识，以JSON格式输出，"
#     "JSON必须包含以下字段：setup(这个小知识的摘要)、"
#     "core(这个小知识的核心内容)、rating(这个小知识的冷门程度，从1-10打分)"))

#绑定结构化输出的“输出格式”（绑定TypedDic）
# model_with_structured=model.with_structured_output(knowledge, method="json_mode")
# print(model_with_structured.invoke(
#     "给我简短的介绍一个有用的小知识，以JSON格式输出，"
#     "JSON必须包含以下字段：setup(这个小知识的摘要)、"
#     "core(这个小知识的核心内容)、rating(这个小知识的冷门程度，从1-10打分)"))

#绑定结构化输出的“输出格式”（绑定JSON）
#注意：with_structured_output默认method是json_schema，DeepSeek不支持；
#必须显式指定method="json_mode"，且提示词里要写明字段
model_with_structured=model.with_structured_output(json_schema, method="json_mode")
print(model_with_structured.invoke(
    "给我简短介绍一个有用的小知识,以JSON格式输出，"
    "JSON必须包含以下字段：setup(这个小知识的摘要)、"
    "core(这个小知识的核心内容)、rating(这个小知识的冷门程度，从1-10打分)"))