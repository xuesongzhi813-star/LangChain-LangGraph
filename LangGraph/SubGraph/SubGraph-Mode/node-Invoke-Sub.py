from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph


#定义子图

class SubState(TypedDict):
    sub1:str #作为输入
    sub2:str

def sub_node1(state: SubState):
    return {"sub1":state["sub1"]+" hi!this is sub1 "}

def sub_node2(state: SubState):
    return {"sub2":state["sub1"]+" And it's sub2 "}

sub_Builder=StateGraph(SubState)
sub_Builder.add_sequence([sub_node1,sub_node2])
sub_Builder.add_edge(START,"sub_node1")

sub_Graph=sub_Builder.compile()


#定义主图(在节点中调用子图)

class State(TypedDict):
    start:str #作为输入
    result:str #作为输出

def node1(state: State):
    return {"start":"it's "+state["start"]}

def node2(state: State):
    '''调用子图'''
    result=sub_Graph.invoke({"sub1":"主图开始调用子图"})
    return {
        "result":state["start"]+result["sub2"]+" 主图中node2执行完毕了"
    }

builder=StateGraph(State)
builder.add_sequence([node1,node2])
builder.add_edge(START,"node1")
graph=builder.compile()

# print(graph.invoke({"start": "主图开始执行了"}))
#使用“流式输出”打印结果
for chunk in graph.stream({"start": "主图开始执行了"},stream_mode="updates",subgraphs=True):
    print(chunk)



