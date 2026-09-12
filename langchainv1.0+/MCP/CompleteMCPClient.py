import asyncio
import os

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool
from langchain_openai import ChatOpenAI


async def main():
    client=MultiServerMCPClient(
        {
        "DocumentStore":{
            "transport":"stdio",
            "command":"python",
            "args":["D:\LangChain\LangChain-LangGraph\langchainv1.0+\MCP\CompleteMCPServer.py"]
        },
        }
    )

    #加入了MCP的Agent的流程：
    #关于资源如何使用：资源的作用：本质是“给LLM提供上下文信息”，供给LLM查询-->根据查到资源分类-->定义处理这些类的工具-->工具绑定Agent

    async with client.session("DocumentStore") as session:
        Blobs=await client.get_resources("DocumentStore")

        #将资源转化成工具，方便agent检索
        @tool
        def get_guide(query:str)->str:
            '''获取文件系统资源'''
            results=[]
            for blob in Blobs:
                if blob.mimetype=="text/plain":
                    content=blob.as_string()
                    print("当前文档内容:"+content)
                    results.append(content)
            return "\n\n".join(results) if results else "未找到相关文档"

        @tool
        def get_fag(query:str)->str:
            '''获取重置密码的方法的资源'''
            results=[]
            for blob in Blobs:
                if blob.mimetype=="text/plain":
                    content=blob.as_string()
                    print("当前文档内容:"+content)
                    results.append(content)
            return "\n\n".join(results) if results else "未找到相关文档"

        model=ChatOpenAI(
            model="deepseek-v4-flash",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        )

        agent=create_agent(
            model=model,
            system_prompt="你是一个乐于助人的助手，解决问题时，尽量使用工具",
            tools=[get_guide,get_fag]
        )

        result=await agent.ainvoke(
            {"messages":[{"role":"user","content":"如何进行文件系统操作?"}]}
        )
        print(result)



if __name__ == "__main__":
    asyncio.run(main())














