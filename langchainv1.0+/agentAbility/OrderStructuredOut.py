import os

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from openai import BaseModel

#定义模型
#因为ds不支持提供者策略，因此，示例采用工具策略
model = ChatOpenAI(model="deepseek-v4-flash", api_key=os.getenv("DEEPSEEK_API_KEY"),
                   base_url="https://api.deepseek.com",extra_body={"thinking": {"type": "disabled"}},
#关闭思考模式，否则无法调用工具
)

#定义结构化输出
#注意：字段要有默认值，避免模型返回null/缺字段时pydantic校验失败
class StructuredOut(BaseModel):
    name: str = ""
    phone_number: str = ""
    location: str = ""
    weather: str = ""

#采用tool策略
agent=create_agent(
    model=model,
    response_format=ToolStrategy(StructuredOut),
    #注意：不要在提示词里让模型“返回None”，模型会把Python字面量None写进JSON参数，
    #导致非法JSON，进而引发"insufficient tool messages"的400报错
    system_prompt="从中提取出这个人的信息特征，无法确定的字段返回空字符串",
)

#打印
result=agent.invoke(
    {"messages":[{"role":"user","content":"小明在一个天气晴朗的日子出发去东方明珠玩"}]}
)
structured_response=result["structured_response"]
print(structured_response)
