import os

from langchain_openai import ChatOpenAI

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}}, #关闭思考模式->使用结构化输出
)