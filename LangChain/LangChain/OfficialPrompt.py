# Create a LangSmith API in Settings > API Keys
# Make sure API key env var is set:
# import os; os.environ["LANGSMITH_API_KEY"] = "<your-api-key>"
import os

from langchain_openai import ChatOpenAI
from langsmith import Client

from LangChain.test1 import chain

client = Client()
prompt = client.pull_prompt("hardkothari/prompt-maker",include_model=True,dangerously_pull_public_prompt=True)

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

chain=prompt | model

while True:
    task=input("\n 请输入你的任务 \n")
    if task=="exit":
        break
    lazy_prompt=input("\n 请输入简化的提示词 \n")
    if lazy_prompt=="exit":
        break
    #执行官方提示词
    chain.invoke({"task":task,"lazy_prompt":lazy_prompt}).pretty_print()