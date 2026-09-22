import os

from tokenizers import Tokenizer

from langchain_core.messages import trim_messages, BaseMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph

model = ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# # 1. 加载 DeepSeek 分词器
# tokenizer = Tokenizer.from_file(
#     os.path.join(os.path.dirname(__file__), "deepseek_tokenizer.json")
# )
#
#
# # 2. 定义自定义 token 计数函数
# def deepseek_token_counter(messages: list[BaseMessage]) -> int:
#     # 将消息列表按 DeepSeek 的对话模板拼接成字符串
#     # 简化示例：实际需按 DeepSeek 的格式（如 <|im_start|> 等）构建
#     text = ""
#     for msg in messages:
#         text += f"{msg.type}: {msg.content}\n"
#
#     # 使用 DeepSeek 分词器编码并返回 token 数
#     return len(tokenizer.encode(text).ids)

#消息裁剪
# def llm_call(state:MessagesState):
#     '''消息裁剪，专门裁剪调用LLM的消息，而非历史消息列表'''
#     message=trim_messages(
#         messages=state["messages"],
#         max_tokens=128,
#         token_counter=deepseek_token_counter,
#         strategy="last",
#         start_on="human",
#         end_on="human",
#     )
#     result = model.invoke(message)
#     return {
#         "messages": [result]
#     }

#消息删除
def llm_call(state:MessagesState):
    '''消息删除，配合return更新状态时，当历史消息数>6时，删除'''
    #执行完，马上删除“历史消息列表”,删除本条/全部
    messages=state["messages"]
    if len(messages) >6:
        return {
            #若更新状态，删除了历史消息列表，会直接返回，不进行后续操作
            "messages":[RemoveMessage(id=msg.id) for msg in messages[:6]],
        }
    result=model.invoke(messages)
    return {
        "messages":[result]
    }


#定义图，添加点，添加边
builder=StateGraph(MessagesState)

builder.add_node(llm_call)

builder.add_edge(START,"llm_call")
builder.add_edge("llm_call",END)

checkpointer=InMemorySaver()
graph=builder.compile(checkpointer=checkpointer)

config={"configurable":{"thread_id":"1"}}
result1=graph.invoke({"messages":[{"role":"user","content":"你好，我叫Leo"}]},config)
result1["messages"][-1].pretty_print()
for msg in result1["messages"]:
    msg.pretty_print()

result2=graph.invoke({"messages":[{"role":"user","content":"请帮我根据“梅花”的主题写一首诗"}]},config)
result2["messages"][-1].pretty_print()
for msg in result2["messages"]:
    msg.pretty_print()

result3=graph.invoke({"messages":[{"role":"user","content":"现在，请帮我把主题切换成“玫瑰”"}]},config)
result3["messages"][-1].pretty_print()
for msg in result3["messages"]:
    msg.pretty_print()

result4=graph.invoke({"messages":[{"role":"user","content":"我是谁？"}]},config)
result4["messages"][-1].pretty_print()
for msg in result4["messages"]:
    msg.pretty_print()










