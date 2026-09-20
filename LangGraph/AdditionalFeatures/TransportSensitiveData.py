from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph

'''
本质：节点之间输入，输出都是状态-->想传递数据就要依附于状态-->自定义状态，传递私密数据
'''


#定义公共状态（全程传递）
class finalState(TypedDict):
    result:str

#定义私密状态-->负责初始传入隐私数据
class SensitiveState(TypedDict):
    sensitive:str

#定义隐私数据传递的状态-->在节点间传递隐私数据
class transportState(TypedDict):
    sensitive_data:str


#定义节点
def node_1(
        state:finalState
)->transportState:
    '''获取隐私数据'''
    print(f"node_1获取到隐私数据")
    return {
        "sensitive_data":f"隐私数据:{state["result"]}"
    }

def node_2(
        state:transportState
)->finalState:
    '''处理隐私数据+生成可见的公共结果'''
    print(f"node_2正在处理隐私数据")
    return {
        "result":f"处理好的结果:{state['sensitive_data']}"
    }

def node_3(
        state:finalState
):
    '''输出最终的结果'''
    print("node_3输出最终结果")
    return {
        "result":f"{state["result"]}+'a'"
    }

builder=StateGraph(finalState)
builder.add_sequence([node_1,node_2,node_3])
builder.add_edge(START,"node_1")

graph=builder.compile()
result=graph.invoke(
    {"result":"1+1+1"}
)
print(result)


