import asyncio

from fastmcp import FastMCP, Context
from pydantic import BaseModel

mcp=FastMCP("Server")

class userDetails(BaseModel):
    age: int
    email: str


@mcp.tool
async def handle_big_file(path:str,ctx:Context)->str:
    '''这是一个处理大文件，并且打印处理进度的工具'''
    print(f"开始处理文件:{path}")

    #！！！核心:打印进度
    #progress:当前进度，total:总量，message:进度描述信息
    await ctx.report_progress(progress=150,total=1000,message="正在读取文档内容……")
    await asyncio.sleep(1)
    await ctx.report_progress(progress=500,total=1000,message="正在处理文档数据计算……")
    await asyncio.sleep(1)
    await ctx.report_progress(progress=750,total=1000,message="正在整理处理结果……")
    await asyncio.sleep(1)
    await ctx.report_progress(progress=1000,total=1000,message="已完成大文件的处理")

    return f"⽂件 {path} 已成功处理。"

@mcp.tool
async def fetch_file(
  query:str,
  ctx: Context,
)->str:
    '''这是一个查询文件的工具'''
    await ctx.info(message="正在查询C盘……")

    await ctx.debug(message="正在验证查询到的信息是否匹配……")

    await ctx.warning(message="验证失败，信息不匹配")

    await ctx.error(message="查询失败")
    return f"关于{query}相关信息查询失败"

#引导式输入：创建一个个人信息档案
@mcp.tool
async def create_user(
        name:str,
        ctx:Context,
)->str:
    '''这是一个创建个人档案的工具（涉及详细信息的补充）'''
    result=await ctx.elicit(message=f"请给我们发送关于用户{name}的详细信息:email+age",response_type=userDetails)
    #判断决策结果，选择不同的创造策略
    if result.action=="accept" and result.data:
        return f"已为用户{name}创建了个人信息档案,email:{result.data.email},age:{result.data.age}"
    elif result.action=="decline":
        return f"已为用户{name}创建了个人信息档案，但是详细数据缺失……"
    return f"已取消关于用户{name}的个人信息档案创建"



if __name__=="__main__":
    mcp.run(transport="streamable-http")