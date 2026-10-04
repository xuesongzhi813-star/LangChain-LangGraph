from langgraph.constants import END
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from typing_extensions import TypedDict


class State(TypedDict):
    foo: str
# ⼦图
def subgraph_node_1(state: State):
    print("sub_node_1")
    return {}

def subgraph_node_2(state: State):
    print("sub_node_2")
    value = interrupt("输⼊值:")
    return {"foo": state["foo"] + value}

subgraph_builder = StateGraph(State)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()
# 主图
def node_1(state: State):
    print("node_1")
    return {}
    #下面注释，是用于节点中调用子图情况时
    # response = subgraph.invoke({"foo": state["foo"]})
    # return {"foo": response["foo"]}


#“子图作为节点”的方式-->此时主，子图中的同名字段，是互通的
builder = StateGraph(State)
builder.add_node(node_1)
builder.add_node("node_2",subgraph)

builder.add_edge(START, "node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2",END)
graph = builder.compile(checkpointer=InMemorySaver())
config={"configurable":{"thread_id":"111"}}
print(graph.invoke({"foo": "bar"},config=config))
#在“子图作为节点”的模式中，“中断”的恢复只是重新执行了“子图节点”
print(graph.invoke(Command(resume="你好"),config=config))



#在“节点”中调用子图的方式-->此时主，子图中的“同名字段”并不是互通的，是相互独立的
# builder = StateGraph(State)
# builder.add_node("node_1", node_1)
# builder.add_edge(START, "node_1")
# graph = builder.compile(checkpointer=InMemorySaver())
# config={"configurable":{"thread_id":"111"}}
# print(graph.invoke({"foo": "bar"},config=config))
# #“节点中调用子图”的模式中，“中断”的恢复，会重新执行:“调用子图的节点”+“子图”
# print(graph.invoke(Command(resume="你好"),config=config))
