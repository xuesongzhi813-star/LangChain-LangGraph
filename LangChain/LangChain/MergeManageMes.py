from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, merge_message_runs

messages = [
SystemMessage("你是一个聊天助手。"),
SystemMessage("你总是以笑话回应。"),
HumanMessage("为什么要使用 LangChain?"),
HumanMessage("为什么要使用 LangGraph?"),
AIMessage("因为当你试图让你的代码更有条理时，LangGraph 会让你感到“节点”是个好主意！"),
AIMessage("不过别担心，它不会“分散”你的注意力！"),
HumanMessage("选择LangChain还是LangGraph?"),
]

merge_message_runs(
    messages=messages,
)

#[SystemMessage(content='你是一个聊天助手。\n你总是以笑话回应。', additional_kwargs={}, response_metadata={}),
# HumanMessage(content='为什么要使用 LangChain?\n为什么要使用 LangGraph?', additional_kwargs={}, response_metadata={}),
# AIMessage(content='因为当你试图让你的代码更有条理时，LangGraph 会让你感到“节点”是个好主意！\n不过别担心，它不会“分散”你的注意力！', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]),
# HumanMessage(content='选择LangChain还是LangGraph?', additional_kwargs={}, response_metadata={})]
print(merge_message_runs(
    messages=messages,
))