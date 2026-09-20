import operator
from typing import TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Overwrite


class MessageState(TypedDict):
    messages:Annotated[list[str],operator.add] #追加更新的状态

#定义节点
def add_node(
        state: MessageState,
):
    return {
        "messages":["add message"]
    }

def replace_node(
        state: MessageState,
):
    '''使用Overwrite不再进行追加，而是重写成一个新的-->类似直接替换'''
    return {
        "messages":Overwrite(["replace message"])
    }
    # return {
    #     "messages":["replace message"]
    # }

builder=StateGraph(MessageState)
builder.add_node("add_node",add_node)
builder.add_node("replace_node",replace_node)
builder.add_edge(START,"add_node")
builder.add_edge("add_node","replace_node")
builder.add_edge("replace_node",END)

graph=builder.compile()
result=graph.invoke(
    {"messages":["start"]}
)
print(result["messages"])