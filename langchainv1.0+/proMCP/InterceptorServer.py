from fastmcp import FastMCP

mcp=FastMCP("server1.0")

@mcp.tool
async def search_weather(city:str,user_id:str)->str:
    '''用户查询天气'''
    return f"用户{user_id}查询到{city}的天气为:晴空万里"

@mcp.tool
async def login(user_name:str)->str:
    '''用户登录'''
    return f"用户{user_name}登录成功"

@mcp.tool
async def mutiply(a:float,b:float)->float:
    '''计算乘法'''
    return a*b

@mcp.tool
async def add(a:float,b:float)->float:
    '''计算加法'''
    return a+b


if __name__ == "__main__":
    mcp.run(transport="streamable-http",port=8000)