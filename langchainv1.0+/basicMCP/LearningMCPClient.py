import asyncio
import json
import os

from langchain.agents import create_agent
from langchain_core.documents.base import Blob
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from mcp_types import TextContent


#定义“结果拦截器”-->这个的功能：拼接一段新属性
#“持久化会话”条件下无效，要“无状态”条件下才行
async def append_state(request:MCPToolCallRequest,handler):
    result=handler(request)
    #如果有“结构化结果”
    if result.structuredContent:
        result.content+=[
            TextContent(type="text",text=json.dumps(result.structuredContent))
        ]
    return result

#定义“持久化会话”的
async def main():
    client = MultiServerMCPClient(
        {"learning_server": {
            "transport": "stdio",
            "command": "python",
            "args": ["D:\LangChain\LangChain-LangGraph\langchainv1.0+\MCP\LearningMCPServer.py"]
        }
        },
        tool_interceptors=[append_state],
    )

    async with client.session("learning_server") as session:

        tools=await client.get_tools()
        print(tools)
        #知识点1：按照“结构化”获取结果

#######################################资源+提示词###################################################
        #获取资源（获取服务器的所有资源）
        #若是“无状态”对话，仍然参数填写“服务器名”即可
        # Blobs=await client.get_resources("learning_server")
        # for blob in Blobs:
        #     print(f"[获取所有资源]资源的基本数据有:uri:{blob.metadata['uri']}")
        #     print(f"[获取所有资源]资源的数据类型是:{blob.mimetype}")
        #     print(f"[获取所有资源]资源的内容是:{blob.as_string()}")

        # 获取资源（获取指定uri资源）
        # 若是“无状态”对话，仍然参数填写“服务器名”+要获取的资源的“uris列表”
        Blobs=await client.get_resources("learning_server",uris=["data://config"])
        for blob in Blobs:
            print(f"[获取指定uri资源]资源的基本数据有:uri:{blob.metadata['uri']}")
            print(f"[获取指定uri资源]资源的数据类型是:{blob.mimetype}")
            print(f"[获取指定uri资源]资源的内容是:{blob.as_string()}")

        #获取提示词
        #返回的是List[Messages]
        messages=await client.get_prompt("learning_server","generate_code_request",
                               arguments={
                                    "language":"一段搜索关键词","task_description":"查询当地的天气"
                                })
        for message in messages:
            print(message.type+":"+message.text)


        #定义model
        model=ChatOpenAI(
            base_url="https://api.deepseek.com",
            model="deepseek-v4-flash",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        )

        #定义agent
        agent=create_agent(
            model=model,
            system_prompt="解决问题时，优先采用工具解决",
            tools=tools,
        )

        #######################################工具###################################################
        weather_result=await agent.ainvoke(
            {"messages":[{"role":"user","content":"南京的天气怎么样？"}]}
        )

        #工具知识点1：拿到结构化的结果
        #结果:{'result':'南京总是晴空万里'}
        # for something in weather_result["messages"]:
        #     if isinstance(something,ToolMessage) and something.artifact:
        #         print(something.artifact["structured_content"])

        #工具知识点2：工具拦截器，可以对返回的结果中“增添属性”/“拦截”
        #类似于“包装方式”定义工具中间件
        print(weather_result)

if __name__ == "__main__":
    asyncio.run(main())
