from fastmcp import FastMCP

#定义MCP
mcp=FastMCP("weather_server")

#构建工具
@mcp.tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"

if __name__ == "__main__":
    #天气MCP服务器，由网络通信
    mcp.run(transport="streamable-http",port=8000)