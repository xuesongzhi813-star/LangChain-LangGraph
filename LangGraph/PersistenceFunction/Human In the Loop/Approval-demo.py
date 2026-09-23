'''基于“人机交互”实现的：任务审批/拒绝'''
from typing import TypedDict, Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


#定义状态
class State(TypedDict):
    action:str
    strategy:Literal["阻塞审批","批准","拒绝"]
    result:str | None

#定义节点
def strategy_node(state:State):
    '''审批/拒绝当前任务的节点'''
    response=interrupt(
        {
            "action":f"本次执行的业务是:{state["action"]}",
            "question":"本次业务审批：批准/拒绝，请输入"
         }
    )

    if response["strategy"] =="批准":
        return Command(goto="approval_node")
    else:
        return Command(goto="reject_node")


def approval_node(state:State):
    '''批准任务的节点'''
    return {
        "strategy": "批准",
        "result": f"本次业务{state['action']}，已批准，执行完毕"
    }

def reject_node(state:State):
    '''拒绝任务的节点'''
    return {
        "strategy": "拒绝",
        "result": f"本次业务{state['action']}，已被拒绝执行，业务结束"
    }

#定义图，添加点，添加边
builder=StateGraph(State)

builder.add_node(strategy_node)
builder.add_node(approval_node)
builder.add_node(reject_node)

builder.add_edge(START,"strategy_node") #因为有goto，不用添加“条件边”抉择走向
builder.add_edge("approval_node",END)
builder.add_edge("reject_node",END)

graph=builder.compile(checkpointer=InMemorySaver())

config={"configurable":{"thread_id":"1"}}
result1=graph.invoke({"action":"转账500元","strategy":"阻塞审批"},config=config)
print(result1)

result2=graph.invoke(Command(resume={"strategy":"拒绝"}),config=config)
print(result2)
