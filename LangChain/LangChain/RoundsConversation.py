import os

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langgraph.graph.message import Messages

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#LLM并没有记忆-->就算是先后顺序的调用它也不会有记忆
# model.invoke("I am Bob,Hi").pretty_print()
# model.invoke("我是谁").pretty_print()
#多轮会话的本质-->将上下文打包给LLM

#打包“介绍自己”的上下文
# messages=[
#     HumanMessage("I am Bob,Hi"),
#     AIMessage("Hi Bob! 👋 How can I help you today?"),
#     HumanMessage("我是谁？")
# ]
#
# #调用LLM
# model.invoke(messages).pretty_print()

#使用“内存缓存”实现“多轮对话”
store={}
def get_session_history(session_id:str)->BaseChatMessageHistory:
    #InMemoryChatMessageHistory将历史消息存储在内存中
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

#包装model，将消息历史记录和模型封装
with_history_message_model=RunnableWithMessageHistory(model,get_session_history)
config = {"configurable":{"session_id":"1"}}

#历史消息设置
print(with_history_message_model.invoke(
    [HumanMessage("Hi,I am Bob!")],
    config=config,
))

#本轮对话消息
print(with_history_message_model.invoke(
    [HumanMessage("Who I am?")],
    config=config,
))