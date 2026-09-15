from fastmcp import FastMCP

# from mcp.server.fastmcp import FastMCP
mcp=FastMCP("Math-Server")

@mcp.tool
def add(a: int, b: int) -> int:
    """执行“数字求和”的工具"""
    return a+b
@mcp.tool
def mutiply(a: int, b: int) -> int:
    '''执行“数字相乘”的工具'''
    return a*b

if __name__ == "__main__":
    #MCP数学服务器，由线程传输
    mcp.run(transport="stdio")