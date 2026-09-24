import os
from dataclasses import dataclass
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langchain.tools import tool, ToolRuntime
from langchain.messages import AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.config import get_stream_writer
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_name: str = ""


@dataclass
class Context:
    user_id: str
@tool
def search(runtime: ToolRuntime[Context]) -> str:
    """调⽤搜索⼯具"""
    user_id = runtime.context.user_id  # 访问上下⽂
    user_name = runtime.state["user_name"]  # 访问状态
    # 获取流式写⼊器
    writer = get_stream_writer()
    # 发送开始信号
    writer({
        "type": "search_tool",
        "status": "start",
        "user_id": user_id,
        "user_name": user_name
    })
    # 模拟搜索过程
    writer({
        "type": "search_tool",
        "status": "searching",
        "user_id": user_id,
        "user_name": user_name
    })
    # 模拟处理时间
    import time
    time.sleep(2)
    # 结束
    writer({
        "type": "search_tool",
        "status": "end",
        "user_id": user_id,
        "user_name": user_name
    })
    return f"查询天⽓：晴天，15-20度"  # 模拟调⽤


# 绑定⼯具
model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
with_tool_model=model.bind_tools([search])

def llm_call(state: dict):
    """LLM决定是否调⽤⼯具"""
    # 获取流式写⼊器
    writer = get_stream_writer()
    # 发送开始处理的信号
    writer({
        "type": "llm_call",
        "status": "start",
        "message": "开始调⽤LLM",
        "content": state["messages"][-1].content
    })
    result = with_tool_model.invoke(
        [SystemMessage(content="你是⼀个乐于助⼈的助⼿，⽀持调⽤⼯具进⾏搜索。")]
        + state["messages"]
    )
    # 调⽤结束
    writer({
        "type": "llm_call",
        "status": "end",
        "message": "调⽤LLM完成"
    })
    return {"messages": [result]}

# 定义并编译图
builder = StateGraph(MessagesState, context_schema=Context)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", ToolNode([search]))
builder.add_edge(START, "llm_call")
builder.add_conditional_edges(
        "llm_call",
        tools_condition,
        {
            "tools": "tool_node",  # 将条件输出转换为图中的节点
            "__end__": END,
        }, )
builder.add_edge("tool_node", "llm_call")
graph = builder.compile()
for chunk in graph.stream(
        {
                "messages": [HumanMessage(content="今天西安的天⽓如何？")],
                "user_name": "⼩明"
        },
        context={"user_id": "123"},
        stream_mode=["custom"]
):
    print(chunk)