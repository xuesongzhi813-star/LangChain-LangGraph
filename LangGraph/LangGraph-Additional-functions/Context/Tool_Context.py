import operator
import os
from dataclasses import dataclass
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolRuntime, ToolNode, tools_condition


#定义“静态上下文”
@dataclass
class ContextSchema:
    user_id:str

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#定义“状态”
class State(TypedDict):
    user_name: str
    messages:Annotated[list[AnyMessage],operator.add] #更新

#定义“查询天气的工具”
@tool
def search_weather_tool(runtime:ToolRuntime[ContextSchema]):
    '''查询天气的工具'''
    user_id=runtime.context.user_id
    user_name=runtime.state["user_name"]
    print(f"【日志打印】:用户:{user_id}:{user_name},正在进行天气的查询")
    return f"天气多云，温度12-16℃"


with_tool_model=model.bind_tools([search_weather_tool])

#定义节点
def llm_call_node(state:State):
    '''llm处理用户问题的节点'''
    return {
        "messages":[with_tool_model.invoke([SystemMessage(content="你是一名乐于助人的助手，支持工具的调用")]
                                           +state["messages"])]
    }

builder=StateGraph(State,context_schema=ContextSchema)

builder.add_node(llm_call_node)
builder.add_node("tool_node",ToolNode([search_weather_tool]))


builder.add_edge(START,"llm_call_node")
builder.add_conditional_edges("llm_call_node",tools_condition,
                              {
                                  "tools":"tool_node",
                                  "__end__":END
                              })
builder.add_edge("tool_node","llm_call_node")

graph=builder.compile()

result=graph.invoke(
    {"messages":[HumanMessage(content="今天南京的天气怎么样")],"user_name":"小明"},
    context={"user_id":"1"}
)
print(result)

for msg in result["messages"]:
    msg.pretty_print()











