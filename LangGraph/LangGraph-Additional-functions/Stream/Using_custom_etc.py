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
    search_steps = [
        {"name": "搜索1", "time": 1, "result": "晴天，"},
        {"name": "搜索2", "time": 2, "result": "15-20度"},
    ]
    all_result = "查询天⽓："
    import time
    for i, step in enumerate(search_steps, 1):
        writer({
            "type": "search_tool",
            "status": "searching",
            "step": step['name'],
            "all_step": len(search_steps),
            "cur_step": i,
            "user_id": user_id,
            "user_name": user_name
        })
    # 模拟处理时间
    time.sleep(step['time'])
    all_result += step['result']
    # 结束
    writer({
        "type": "search_tool",
        "status": "end",
        "user_id": user_id,
        "user_name": user_name,
        "result": all_result
    })
    return all_result



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

# 运⾏并监控⾃定义流
print("图开始执⾏：")
for chunk in graph.stream(
{
"messages": [HumanMessage(content="今天西安的天⽓如何？")],
"user_name": "⼩明"
},
context={"user_id": "123"},
stream_mode=["custom", "updates"]
):
    if chunk[0] == "custom":  # ⾃定义监控，可以输出到⽂件
        info = chunk[-1]
        if info.get("type") == "llm_call":
            pass
        elif info.get("type") == "search_tool":
            status = info.get("status")
            if status == "start":
                print(f"⽤⼾id:{info['user_id']}, ⽤⼾名称:{info['user_name']}开始调⽤⼯具...")
            elif status == "searching":
                print(f"[{info['cur_step']}/{info['all_step']}] 正在处理:{info['step']}")
            elif status == "end":
                print(f"调⽤完成！结果: {info['result']}")
    elif chunk[0] == "updates":  # 正常输出到终端
        pass



