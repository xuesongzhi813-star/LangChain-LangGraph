'''基于“人机交互”实现验证人工输入信息'''
import operator
from typing import TypedDict, Annotated


#基本功能：注册一个会员
#注册会员的基本信息？姓名+年龄+邮箱

#定义状态
class State(TypedDict):
    messages:Annotated[list[str],operator.add]

#定义节点