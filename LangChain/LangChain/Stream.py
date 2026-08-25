import asyncio
import os

from langchain_openai import ChatOpenAI

#定义模型
model=ChatOpenAI(
model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#进行流式输出
#1.先定义一个链表
# chunks=[]
#
# #进行遍历流式输出的“块”，实现流式输出
# for chunk in model.stream("帮我生成5句情诗"):
#     chunks.append(chunk)
#     print(chunk.content,end="|",flush=True)
# print(chunks[0]+chunks[1]+chunks[2]+chunks[3]+chunks[4]+chunks[5])

#进行异步的流式输出
#先定义一个链表
chunks=[]

#定义一个“协程”
async def streamOut():
    async for chunk in model.astream("帮我生成5句情诗"):
        chunks.append(chunk)
        print(chunk.pretty_print(),end="|",flush=True)

#开启协程
asyncio.run(streamOut())

