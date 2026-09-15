import asyncio
import os
from dataclasses import dataclass

from langchain.agents import create_agent, AgentState
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

@dataclass
class Context:
    user_id:str
    api_key:str

class AgentS(AgentState):
    auth:bool=False


#使用“工具拦截器”只能是“无状态”
#定义方位上下文的“工具拦截器”
# async def get_context(
#         request:MCPToolCallRequest,
#         handler
# ):
#     #前置操作:工具执行前设置
#     #获取“上下文”
#     Runtime=request.runtime
#     #注入MCP工具调用
#     user_id=Runtime.context.user_id
#     api_key=Runtime.context.api_key
#     request=request.override(args={**request.args,"user_id":user_id})
#     return await handler(request) #handler就是工具开始执行
#
# #定义状态更新与流程
# async def update_auth(
#         request:MCPToolCallRequest,
#         handler
# )->ToolMessage | Command:
#     #先根据，授权状态筛选
#     #后置操作：工具执行后操作
#     runtime=request.runtime
#     return Command(
#         update={"messages": [ToolMessage(content="直接结束", tool_call_id=runtime.tool_call_id)]},#更新状态
#         goto="__end__"
#
#     )

#打印日志的“工具拦截器”
# async def print_login(
#     request:MCPToolCallRequest,
#     handler
# ):
#     print(f"工具调用前,工具名称:{request.name},工具参数:{request.args}")
#     result=await handler(request)
#     print(f"工具调用后,结果:{result}")

# #修改“工具参数”的“工具拦截器”
# async def modify_args(
#         request:MCPToolCallRequest,
#         handler
# ):
#     request=request.override(args={k:v+2 for k,v in request.args.items()})
#     return await handler(request)

#错误处理与重试
# async def retry(
#         request:MCPToolCallRequest,
#         handler,
#         max_retries=3,
#         delay=1,
# ):
#     """重试失败的⼯具调⽤，采⽤指数退避策略。"""
#     last_error = None
#     for attempt in range(max_retries):
#         try:
#             return await handler(request)
#         except Exception as e:
#             last_error = e
#             if attempt < max_retries - 1:
#                 wait_time = delay * (2 ** attempt)  # 计算指数退避等待时间
#             print(f"Tool {request.name} failed (attempt {attempt + 1}),retrying in {wait_time}s...")
#             await asyncio.sleep(wait_time)
#             raise last_error  # 所有重试均失败后，抛出最后的异常0

#错误降级处理
# async def fallback_interceptor(
# request: MCPToolCallRequest,
# handler,
# ):
#     """如果⼯具执⾏失败，返回⼀个降级响应。"""
#     try:
#         return await handler(request)
#     except TimeoutError:
#         return f"Tool {request.name} timed out. Please try again later."
#     except ConnectionError:
#         return f"Could not connect to {request.name} service. Using cacheddata."





async def main():

    client=MultiServerMCPClient(
        {"server1.0":{
            "transport":"streamable-http",
            "url":"http://127.0.0.1:8000/mcp"
        }},
        tool_interceptors=[],

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
            tools=tools,
            context_schema=Context,
            state_schema=AgentS,
        )

    result= await agent.ainvoke(
            {"messages":[{
                # "role":"user","content":"今天南京的天气怎么样"
                "role":"user","content":"请计算1+5的结果，优先调用工具解决"
            },
                ]},
        context={"user_id":"111","api_key":"sk-"},
        )
    print(result)



if __name__ == '__main__':
    asyncio.run(main())