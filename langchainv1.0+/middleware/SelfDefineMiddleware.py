import os
from typing import Any, Callable

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_agent, after_agent, before_model, after_model, wrap_model_call, \
    ModelRequest, ModelResponse, wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langchain.tools import tool
from langgraph.types import Command

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)



#定义工具
@tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"

#装饰器方式：节点风格，创建中间件
@before_agent
def before_agent(state: AgentState,runtime: Runtime)->dict[str,Any] | None:
    """参数：状态+上下文"""
    print("在agent执行之前……")
    return None

@after_agent
def after_agent(state: AgentState,runtime: Runtime)->dict[str,Any]|None:
    """参数：状态+上下文"""
    print("在agent执行之后……")
    return None

@before_model
def before_model(state: AgentState,runtime: Runtime)->dict[str,Any] | None:
    """参数：状态+上下文"""
    print("在model执行之前……")
    return None

@after_model
def after_model(state: AgentState,runtime: Runtime)->dict[str,Any] | None:
    """参数：状态+上下文"""
    print("在model执行之后……")
    return None

#装饰器方式：包装风格，自定义中间件
@wrap_model_call
def wrap_model_call(
        request:ModelRequest,
        handler:Callable[[ModelRequest],ModelResponse],
)->ModelResponse:
    print("[wrap model模型调用前]")
    print(f"当前model请求的状态{request.state}")
    print(f"模型的最新消息:{request.messages[-1].content}")
    for i in range(3):
        try:
            response=handler(request)
            print("[wrap model]模型调用成功")
            return response
        except Exception as e:
            if i==2:
                raise
            print(f"模型已经尝试执行第{i+1}次，剩余执行次数{2-i}")

@wrap_tool_call
def wrap_tool_call(
        request:ToolCallRequest,
        handler:Callable[[ToolCallRequest],ToolMessage | Command],
)->ToolMessage | Command:
    print("[wrap tool]在tool执行之前")
    print(f"当前执行的tool:{request.tool_call['name']}")
    print(f"当前执行的tool的参数:{request.tool_call['args']}")
    try:
        response=handler(request)
        print("[wrap tool]工具调用成功")
        return response
    except Exception as e:
        print(e)

agent=create_agent(
    model=model,
    middleware=[before_agent, after_agent, before_model, after_model, wrap_model_call, wrap_tool_call],
    tools=[search_for_weather],
)

print(agent.invoke(
    {"messages": [{"role": "user", "content": "南京今天的天气如何"}]}
))
