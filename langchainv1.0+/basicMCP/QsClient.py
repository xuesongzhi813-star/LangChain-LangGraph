import asyncio
import os

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

async def main():
    # cilent实际上是异步的
    client = MultiServerMCPClient(
        {
            # 添加要连接的服务器
            "weather_server": {
                # 传输方式为“网络通信”的服务器参数：
                # 1.传输方式 2.url
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8000/mcp",
            },
            "Math-Server": {
                # 传输方式为“线程传输”的服务器参数：
                # 1.传输方式 2.command语言 3.服务器所在的绝对路径
                "transport": "stdio",
                "command": "python",
                "args": [r"D:\LangChain\LangChain-LangGraph\langchainv1.0+\MCP\QsMathServer.py"]
            }
        }
    )
    # 设置session持久化对话
    async with client.session("weather_server") as session:  # 持久会话（进入时已自动 initialize）
        tools = await load_mcp_tools(session)  # 从该会话中加载工具
        # tools=await client.get_tools()
        print(tools)

        # 定义模型model
        model = ChatOpenAI(
            model="deepseek-v4-flash",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        )

        agent = create_agent(
            model=model,
            system_prompt="你是一共乐于助人的AI助手，你执行的操作尽量调用工具实现",
            tools=tools,
        )

        weatehr_result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "今天南京的天气如何?"}]}
        )
        math_result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "5*7*(4+3)等于多少"}]}
        )
        print(weatehr_result)
        print(math_result)



if __name__ == "__main__":
    asyncio.run(main())
