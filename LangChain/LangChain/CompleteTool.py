from typing import Annotated

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


#1.定义工具
@tool
def add(
        a:Annotated[int,"第一个参数"],
        b:Annotated[int,"第二个参数"],
)->int:
    '''两数相加'''
    return a+b;

@tool
def multiply(
        a:Annotated[int,"第一个参数"],
        b:Annotated[int,"第二个参数"],
)->int:
    '''两数相乘'''
    return a*b;

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
api_key="sk-d42eb96c922047c9bd84615ee700b393")

#仅当直接运行本文件时才执行，被其他文件import时不会触发
if __name__ == "__main__":
    #定义问题
    messages=[
        HumanMessage("6+6等于几？12*8等于几")
    ]

    #2.绑定工具
    tools=[add,multiply]
    bind_tool_model=model.bind_tools(tools)

    #3.调用工具:选择工具+真正调用工具
    #选择工具
    ai_message=bind_tool_model.invoke(messages)
    messages.append(ai_message)

    #调用工具（根据选择的工具信息，来调用）
    for tool_call in ai_message.tool_calls:
        selected_tool = {"add": add, "multiply": multiply}[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)

    #问题+工具绑定+工具选择-->总的消息-->得到最终的问答式结果
    print(model.invoke(messages).content)
