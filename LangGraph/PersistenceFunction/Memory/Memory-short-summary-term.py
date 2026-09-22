import os

from click import prompt
from langchain_core.messages import HumanMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#定义状态
class State(MessagesState):
    summary:str

#定义节点
def llm_call(state:State):
    '''负责llm调用处理问题'''
    summary=state.get("summary","")
    message=state["messages"]
    Message=(f"这是到目前为止，对话的历史消息的总结:{summary}\n"
             f"请你结合历史消息的总结，和用户新输入的消息{message}，处理任务")
    result=model.invoke([HumanMessage(content=Message)])
    return{
        "messages":[result]
    }

def get_summary(state:State):
    '''负责生成历史消息列表的“总结”，在每次执行完之后'''
    summary=state.get("summary","")
    message=state["messages"]
    if summary:
        #若已经存在summary，则拓展重新生成
        prompt = f"这是到目前为止，对话的历史消息的总结:{summary},请你结合历史消息的总结，和用户新输入的消息{message}，拓展生成一份summary"
        summary=model.invoke([HumanMessage(content=prompt)])
    else:
        #若不存在，直接生成即可
        prompt=(f"请你根据历史消息:{message}，总结出一份摘要")
        summary=model.invoke([HumanMessage(content=prompt)])
    return {
        "summary":summary,
        "messages":[RemoveMessage(id=msg.id) for msg in message[:-1]] #只保留最后一条消息
    }

#定义图，添加点，添加边
builder=StateGraph(State)

builder.add_node(llm_call)
builder.add_node(get_summary)

builder.add_edge(START,"llm_call")
builder.add_edge("llm_call","get_summary")
builder.add_edge("get_summary",END)

checkpointer=InMemorySaver()
graph=builder.compile(checkpointer=checkpointer)

config={"configurable":{"thread_id":"1"}}
result1=graph.invoke({"messages":[{"role":"user","content":"你好，我叫Leo"}]},config)
print(result1["summary"])
for msg in result1["messages"]:
    msg.pretty_print()

result2=graph.invoke({"messages":[{"role":"user","content":"请帮我根据“梅花”的主题写一首诗"}]},config)
print(result2["summary"])
for msg in result2["messages"]:
    msg.pretty_print()

result3=graph.invoke({"messages":[{"role":"user","content":"现在，请帮我把主题切换成“玫瑰”"}]},config)
print(result3["summary"])
for msg in result3["messages"]:
    msg.pretty_print()

result4=graph.invoke({"messages":[{"role":"user","content":"我是谁？"}]},config)
print(result4["summary"])
for msg in result4["messages"]:
    msg.pretty_print()