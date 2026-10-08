from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState

from agent.common.LLM import model


#定义节点:无关租房的其他问题，交由LLM直接回答
def extend_node(state:MessagesState):
    '''调用LLM执行即可'''
    result=model.invoke([SystemMessage(content="你是一个乐于助人的助手，请可能的解决用户提出的问题")]+[state["messages"][-1]])
    return {
        "messages":[result]
    }

