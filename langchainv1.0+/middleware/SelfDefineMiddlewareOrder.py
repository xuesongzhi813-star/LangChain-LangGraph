import os
from typing import Callable, Any

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_agent, after_agent, before_model, after_model, wrap_model_call, \
    ModelRequest, ModelResponse, wrap_tool_call, AgentMiddleware
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
extra_body={"thinking": {"type": "disabled"}},#关闭思考模式，否则无法调用工具
)



#定义工具
@tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"


#用类方式，将所有节点的中间件集合一起
class Middleware1(AgentMiddleware):
    # 装饰器方式：节点风格，创建中间件

    def before_agent(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[1]在agent执行之前……")
        return None

    def after_agent(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[1]在agent执行之后……")
        return None

    def before_model(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[1]在model执行之前……")
        return None

    def after_model(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[1]在model执行之后……")
        return None

    # 装饰器方式：包装风格，自定义中间件

    def wrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        print("[1][wrap model模型调用前]")
        print(f"[1]当前model请求的状态{request.state}")
        print(f"[1]模型的最新消息:{request.messages[-1].content}")
        for i in range(3):
            try:
                response = handler(request)
                print("[1][wrap model]模型调用成功")
                return response
            except Exception as e:
                if i == 2:
                    raise
                print(f"模型已经尝试执行第{i + 1}次，剩余执行次数{2 - i}")


#用类方式，将所有节点的中间件集合一起
class Middleware2(AgentMiddleware):
    # 装饰器方式：节点风格，创建中间件

    def before_agent(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[2]在agent执行之前……")
        return None

    def after_agent(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[2]在agent执行之后……")
        return None

    def before_model(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[2]在model执行之前……")
        return None

    def after_model(self,state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """参数：状态+上下文"""
        print("[2]在model执行之后……")
        return None

    # 装饰器方式：包装风格，自定义中间件

    def wrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        print("[2][wrap model模型调用前]")
        print(f"[2]当前model请求的状态{request.state}")
        print(f"[2]模型的最新消息:{request.messages[-1].content}")
        for i in range(3):
            try:
                response = handler(request)
                print("[2][wrap model]模型调用成功")
                return response
            except Exception as e:
                if i == 2:
                    raise
                print(f"模型已经尝试执行第{i + 1}次，剩余执行次数{2 - i}")



agent=create_agent(
    model=model,
    tools=[search_for_weather],
    middleware=[Middleware1(),Middleware2()],#注意：类方式的中间件必须传实例，不能传类本身
)
config={"configurable":{"thread_id":"1"}}
print(agent.invoke(
    {"messages": [{"role": "user", "content": "今天南京的天气怎么样"}]},
    config=config,
))