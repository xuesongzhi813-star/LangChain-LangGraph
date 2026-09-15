import json

from fastmcp import FastMCP

mcp = FastMCP("DocumentStore")

# 模拟一个文件系统资源
@mcp.resource("file:///help/guide.txt")
def get_guide() -> str:
    return """# 用户指南
1. 首先登录系统
2. 点击“新建项目”
3. 输入项目名称
"""

@mcp.resource("file:///help/faq.json")
def get_faq() -> str:
    return json.dumps({
        "q1": "如何重置密码？",
        "a1": "请点击“忘记密码”链接。"
    })

if __name__ == "__main__":
    mcp.run(transport="stdio")