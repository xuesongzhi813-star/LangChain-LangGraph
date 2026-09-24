import os
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#定义状态
class State(TypedDict):
    topic:str
    joke:str

#定义节点
def topic_node(state:State):
    '''生成笑话的主题的节点'''
    return {
        "topic":model.invoke([HumanMessage(content="帮我生成一个笑话的主题，只需要主题就行")]).content,
    }

def joke_node(state:State):
    '''根据主题，生成对应笑话的节点'''
    return {
        "joke":model.invoke([HumanMessage(content=f"帮我生成一个主题为:{state["topic"]}的笑话")]).content
        }

builder=StateGraph(State)

builder.add_sequence([topic_node,joke_node])

builder.add_edge(START,"topic_node")

graph=builder.compile(checkpointer=InMemorySaver())
config={"configurable":{"thread_id":"1"}}

#第一次进行执行
print(graph.invoke({}, config=config))

#时间旅行
#1.获取历史状态
states=list(graph.get_state_history(config=config))
print(states)

#2.改变历史状态
state=states[1]
print(state.values["topic"])
#到此一切正常


#3.更新状态
# #取出的“状态快照”的线程
new_config=graph.update_state(config=state.config,values={"topic":"关于程序员生活的笑话"})

#4.重放执行（注意：恢复执行必须传 None，传 {} 会被当成新一轮输入、从 topic_node 重新开始）
print(graph.invoke(None, config=new_config))





