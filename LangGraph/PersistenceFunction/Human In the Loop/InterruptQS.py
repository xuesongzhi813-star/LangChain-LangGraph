'''快速介绍Inturrpt的使用'''
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    input:str
    output:str

#定义节点
def response_node(state:State):
    '''中断，等待用户的执行同意'''
    #interrupt参数：向外发送给人工审查的消息
    #interrupt函数返回值：人工干预工作流的结果
    response=interrupt(
        {
            "question":"是否继续执行？",
            "description":"回答yes/no继续接下来的流程"
         }
    )
    if response["decision"]=="yes":
        return {
            "output":"你好，我是你的乐于助人的AI助手"
        }
    else:
        return {
            "output":"任务执行中断，任务结束"
        }



#定义图，添加节点，添加边
builder=StateGraph(State)

builder.add_node(response_node)

builder.add_edge(START,"response_node")
builder.add_edge("response_node",END)

graph=builder.compile(checkpointer=InMemorySaver())

config={"configurable":{"thread_id":"1"}}
result1=graph.invoke({"input":"请帮我调用agent助手"},config=config)
print(result1)

result2=graph.invoke(Command(resume={"decision":"no"}),config=config)
print(result2)