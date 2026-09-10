import os
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_openai import ChatOpenAI
from langchain.tools import tool

#定义模型
modelPro=ChatOpenAI(model="deepseek-v4-pro",api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")
modelFlash=ChatOpenAI(model="deepseek-v4-flash",api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")

#定义中间件，包装风格，更换模型
@wrap_model_call
def wrap_model_call(
        request:ModelRequest,
        handler:Callable[[ModelRequest],ModelResponse],
)->ModelResponse:
    count=len(request.state['messages'])
    if(count>1):
        #当“会话消息”大于5则进行模型修改
        model=modelPro
    else:
        model=modelFlash
    return handler(request.override(model=model))

#定义工具
@tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"

agent=create_agent(
    model=modelFlash,
    middleware=[wrap_model_call],
    tools=[search_for_weather],
)

print(agent.invoke(
    {"messages": [{"role": "user", "content": "今天上海天气如何"}]}
))