from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


class InputState(TypedDict):
    question:str

class OutputState(TypedDict):
    answer:str

class State(InputState,OutputState):
    pass

def answer_node(
        state:InputState,
):
    '''处理输入并生成答案'''
    return {
        "question":state["question"],
        "answer":f"这是{state["question"]}的答案"
    }

#若设置了Input+Output则输出，最终只会返回输出状态的结果，适用于定义API接口，规范输入输出
builder=StateGraph(State,input_schema=InputState,output_schema=OutputState)
builder.add_node("answer_node",answer_node)
builder.add_edge(START,"answer_node")
builder.add_edge("answer_node",END)

graph=builder.compile()

result=graph.invoke(
    {"question":"1+1=?"}
)
print(result)