import asyncio
import os

from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from mcp.client.streamable_http import RequestContext
from mcp.types import LoggingMessageNotificationParams, ElicitRequestFormParams, ElicitResult, ElicitRequestURLParams


#客户端一侧的回调函数：更像是接收结果/完成服务器所需
#定义回调函数（进程打印）
async def get_tool_progress(
        progress:float,
        total:float|None,
        message:str|None,
        context:CallbackContext,#当前调用上下文的元数据（服务器名称，工具名称）
):
    if total:
        percent=progress/total*100
        print(f"当前项目已经处理进度:{percent}%")
    else:
        print(f"当前进度:{progress}，{message}")

#定义回调函数（日志记录）
async def on_logging_message(
        params:LoggingMessageNotificationParams,
        ctx: CallbackContext,
):
    print(f"{ctx.server_name}中:日志级别{params.level}:日志内容{params.data}")

#定义回调函数（引导式输入）
async def on_elicitation(
        ctx: CallbackContext,
        params:ElicitRequestURLParams,
        mcp_ctx:RequestContext
)->ElicitResult:
    """处理来⾃ MCP 服务器的引导请求"""
    # 实际应⽤中，此处应根据 params.message 和 params.requestedSchema 提⽰真实⽤⼾输⼊
    #直接返回决策策略+信息即可
    return ElicitResult(
        action="accept",
        content={"email": "user@example.com", "age": 25},
    )





async def main():
    client=MultiServerMCPClient(
        {"Server":{
            "transport":"streamable-http",
            "url":"http://127.0.0.1:8000/mcp",
        }},
        tool_interceptors=[],
        callbacks=Callbacks(on_progress=get_tool_progress,on_logging_message=on_logging_message,on_elicitation=on_elicitation),
    )
    tools=await client.get_tools()
    print(tools)
    model=ChatOpenAI(
        model="deepseek-v4-flash",
        base_url="https://api.deepseek.com",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )

    agent=create_agent(
        model=model,
        system_prompt="你是一个乐于助人的助手,解决问题优先调用工具",
        tools=tools,
    )

    response=await agent.ainvoke(
        {"messages":[{"role":"user","content":"请你给我创建一个用户小明的个人信息档案"}]}
    )

    print(response)







if __name__ == "__main__":
    asyncio.run(main())