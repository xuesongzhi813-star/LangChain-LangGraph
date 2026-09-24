import os
from typing import TypedDict
from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
# 定义状态
class State(TypedDict):
    input: str
    output: str

# 初始化模型
model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
def llm_node(state: State):
    """⽣成答案的节点"""
    return {"output": model.invoke([
        {"role": "system", "content": "你是⼀个乐于助⼈的助⼿。"},
        {"role": "user", "content": state["input"]}
    ])
    }

# 构建图
builder = StateGraph(State)
builder.add_node(llm_node)
builder.add_edge(START, "llm_node")
graph = builder.compile()
# 流式输出 LLM Tokens
# 输出格式为(message_chunk, metadata) 元组。
for token_chunk, metadata in graph.stream(
{"input": "请解释什么是机器学习？50字以内"},
stream_mode="messages"
):
    if token_chunk.content:
        # 逐 Token 输出
        print(token_chunk.content, end="", flush=True)


