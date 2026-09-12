import json

from fastmcp import FastMCP
from fastmcp.prompts import Message

mcp=FastMCP("learning_server")

#定义工具
@mcp.tool
def search_weather(city:str)->str:
    return f"{city}总是晴空万里"

#定义资源
#注解括号内填写“获取路径”(uri)
@mcp.resource("data://config")
def get_config() -> str:
    """Provides application configuration as JSON."""
    #按照json的格式返回资源
    return json.dumps({
        "theme": "dark",
        "version": "1.2.0",
        "features": ["tools", "resources"],
    })


#定义提示词
#通过占位符实现“占位”，后续参数构建“提示词模板”
@mcp.prompt
def generate_code_request(language: str, task_description: str) -> list[Message]:
    """Generates a conversation for code generation."""
    return [
        Message(f"Write a {language} function that performs the following task: {task_description}"),
        Message("I'll help you write that function.", role="assistant"),
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")