from typing import TypedDict, Optional

from langgraph.constants import START, END
from langgraph.graph import StateGraph


#定义子图
class SubState(TypedDict):
    sub:str #输入（主图中不存在该键，子图启动时不会有这个值，需在节点里用 get() 兜底）
    parent:str

def sub_node1(state:SubState):
    #主图只传入共享键 parent，sub 键不存在，用 get() 提供默认值，避免 KeyError
    #使用get方法完成了默认值的赋值
    return {"sub":"这是子图专属状态:"+state.get("sub","这是子图的专属数据")}

def sub_node2(state:SubState):
    return {"parent":state["parent"]+",这是主，子图共享状态(经过子图后):"}

sub_Builder=StateGraph(SubState)
sub_Builder.add_sequence([sub_node1,sub_node2])
sub_Builder.add_edge(START,"sub_node1")

sub_Graph=sub_Builder.compile()


#定义主图（子图作为主图的节点）
class State(TypedDict):
    parent:str #主，子图的共享状态

def node1(state:State):
    return {"parent":"这是主，子图共享状态（在主图时）:"+state["parent"]}

builder=StateGraph(State)
builder.add_node(node1)
builder.add_node("node2",sub_Graph) #直接将子图，添加成节点即可
builder.add_edge(START,"node1")
builder.add_edge("node1","node2")
builder.add_edge("node2",END)

graph=builder.compile()
for chunk in graph.stream({"parent":"小明"},stream_mode="updates",subgraphs=True):
    print(chunk)
# print(graph.invoke({"parent":"小明"}))


