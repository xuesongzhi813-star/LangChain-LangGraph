#使用StructuredTool定义工具
#方式一：三要素缺一不可
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


# def add(a:int, b:int)->int:
#     '''
#     两数之和
#     '''
#     return a+b
#
# model_tool=StructuredTool.from_function(add)
# print(model_tool.invoke({"a": 4, "b": 5}))

# 方式二：
#通过from_function中属性来完成“三要素定义”（工具参数要先定义在类中）
class AddInput(BaseModel):
    a:int = Field(description="第一个整数")
    b:int = Field(description="第二个整数")


def add(a: int, b: int) -> int:
    return a + b

add_tool = StructuredTool.from_function(
    func=add,
    name="ADD",             # 工具名
    description="两数相加",   # 工具描述
    args_schema=AddInput,   # 工具参数
)
#仅当直接运行本文件时才执行，被其他文件import时不会触发
if __name__ == "__main__":
    print(add_tool.invoke({"a": 1, "b": 2}))