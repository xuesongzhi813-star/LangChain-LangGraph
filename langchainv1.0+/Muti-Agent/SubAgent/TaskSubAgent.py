import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool

model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",  # 原来拼成 deepsense.com，主机不存在导致 Connection error
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
write_agent=create_agent(model=model,system_prompt="你是一个写作方面的专家")

research_agent=create_agent(model=model,system_prompt="你是一个研究专家")


#定义可以调用的“已注册的代理agent”
#用字典按名字索引：列表只能用整数下标，AGENTS["writer"] 对列表会抛 TypeError
AGENTS={"writer":write_agent,"research":research_agent}

#工具模式实现SubAgent
@tool
def task(
        invoke_agent:str,#调给谁
        request:str #提示词
)->str:
    '''这是一个用于分配任务给不同专业的代理agent执行的工具。
    invoke_agent 可选值: "writer"（写作专家）, "research"（研究专家）'''
    agent=AGENTS[invoke_agent]
    result=agent.invoke(
        {"messages":[{"role":"user","content":request}]}
    )
    #messages 里是 message 对象，取内容用 .content（不要用 ["content"]）
    return result["messages"][-1].content



main_agent=create_agent(
    model=model,
    system_prompt="你负责协调专业⼦代理。"
                  "可⽤代理：research（事实核查），"
                  "writer（内容创作）。"
                  "请使⽤ task ⼯具来分配⼯作。",
    tools=[task],
)
print(main_agent.invoke(
    {"messages": [{"role": "user", "content": "帮我完成一篇有关健身饮食的论文，100字左右"}]}
))