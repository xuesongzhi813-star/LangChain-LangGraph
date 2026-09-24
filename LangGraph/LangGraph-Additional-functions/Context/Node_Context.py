from dataclasses import dataclass
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

'''节点中使用静态上下文'''
#定义一个“静态上下文”
@dataclass
class ContextSchema:
    user_id:str
    langguage:str="en"

#定义一个状态(本质是，动态上下文)
class State(TypedDict):
    messages:list[str]
    user_name:str


#定义节点
def node(state: State,runtime:Runtime[ContextSchema]):
    '''根据“静态上下文”中语言决定输出内容的节点'''
    the_langguage=runtime.context.langguage
    if the_langguage == "en":
        message=f"hello,how are you? 用户:{state["user_name"]}"
    else:
        message=f"你好，最近过的怎么样？ 用户:{state["user_name"]}"

    return {
        "messages":[f"user_id:{runtime.context.user_id},"+message]
    }

builder=StateGraph(State,context_schema=ContextSchema)

builder.add_node(node)

builder.add_edge(START,"node")
builder.add_edge("node",END)

graph=builder.compile()

print(graph.invoke(
    {"messages": "", "user_name": "小明"},
    context={"user_id": "111","langguage": "中文"}
)["messages"]
)


