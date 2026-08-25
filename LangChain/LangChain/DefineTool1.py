from dataclasses import field
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel


#使用@tool注解，定义工具
#1.第一种方法:工具名+工具注释+参数类型都定义在函数中
# @tool
# def add(a:int,b:int)->int :
#     #括号内，规定了调用工具时，传参格式
#     """
#     两数相加：
#     a:第一个整数
#     b:第二个整数
#     """
#     return a+b
#
# #调用工具
# #打印“工具名”+“工具注释”+“参数类型”
# print(add.invoke({"a":4,"b":6}))
# print(add.name)
# print(add.description)
# print(add.args)

#最常用的定义
@tool
def add(
        a:Annotated[int,"第一个整数"],
        b:Annotated[int,"第二个整数"],
)->int:
    '''
    两数之和的工具
    '''
    return a+b


#仅当直接运行本文件时才执行，被其他文件import时不会触发
if __name__ == "__main__":
    print(add.invoke({"a": 4, "b": 5}))
    print(add.name)
    print(add.description)
    print(add.args)