from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilyResearch, TavilySearch
import os

#定义模型
model=ChatOpenAI(base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"))

#定义工具
tool=TavilySearch(max_results=3)

#绑定工具
model_with_tools=model.bind_tools([tool])

#仅当直接运行本文件时才执行，被其他文件import时不会触发
if __name__ == "__main__":
    #定义消息列表
    messages=[
        HumanMessage("北京今天天气如何？")
    ]
    ai_message=model_with_tools.invoke(messages)
    messages.append(ai_message)

    #获取工具执行结果，构造ToolMessage回传模型
    for tool_call in ai_message.tool_calls:
        tool_result=tool.invoke(tool_call["args"])
        tool_message=ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
        messages.append(tool_message)

    print(model.invoke(messages).content)