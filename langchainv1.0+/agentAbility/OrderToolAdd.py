import os
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, AgentMiddleware
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

#定义模型
model=ChatOpenAI(model="deepseek-v4-flash",api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")

#定义工具
@tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"

#定义，要添加的工具
@tool
def calculate_tips(total:float,percent:float=0.1)->float:
    """这是一个计算小费的工具"""
    tips=total*percent
    print(f"小费:{tips},总计消费:{total+tips}")
    return tips

class agentMiddle(AgentMiddleware):
    # 定义，添加工具的中间件
    def wrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        request=request.override(tools=[*request.tools,calculate_tips])
        return handler(request)

    #定义，真正执行新工具的中间件
    def wrap_tool_call(
            self,
            request: ToolCallRequest,
            handler: Callable[[ToolCallRequest],ToolMessage | Command],
    )->ToolMessage | Command:
        if request.tool_call['name']=="calculate_tips":
            request=request.override(tool=calculate_tips)
        else:
            pass
        return handler(request)

agent=create_agent(
    model=model,
    tools=[search_for_weather],
    system_prompt="你是一个ai助手，根据我提供的信息，来回答问题，不知道就说不知道",
    middleware=[agentMiddle()],
)

print(agent.invoke(
    {"messages": [{"role": "user", "content": "我消费的80元一共，需要支付多少小费？"}]}
))