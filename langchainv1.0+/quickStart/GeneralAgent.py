import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
#定义一个模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)


#定义一个供给agent调用的工具
@tool
def search_local_weather(city:str)->str:
    '''查询天气的一个工具'''
    return f"it's always sunny day ,the {city}"


#定义一个agent
agent=create_agent(
    model=model,
    tools=[search_local_weather],
    system_prompt="你是一个帮助我查询信息的助手"
)

result=agent.invoke(
    {"messages":[{"role":"user","content":"what's the weather like in shanghai"}]}
)

#打印状态为messages的
print(result["messages"][-1].content_blocks)